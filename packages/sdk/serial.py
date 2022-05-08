import queue
import signal
import threading
from typing import Optional

from PySide6.QtCore import QObject, Signal
import serial.tools.list_ports
import serial.tools.list_ports_common


def get_available_serial_ports() -> list[serial.tools.list_ports_common.ListPortInfo]:
    return serial.tools.list_ports.comports()


class FreezeDripSerial:
    def __init__(
            self,
            port_name: str,
            input_queue: Optional[queue.Queue] = None,
            output_queue: Optional[queue.Queue] = None):
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.serial: serial.Serial = serial.Serial(port_name, baudrate=115200)
        self.input_queue: Optional[queue.Queue] = input_queue
        self.output_queue: Optional[queue.Queue] = output_queue
        self.stopped: bool = False
        threading.Thread(target=self.receive_loop, daemon=True).start()
        threading.Thread(target=self.send_loop, daemon=True).start()

    def signal_handler(self, signum: int, frame):
        self.stopped = True
        if self.serial and self.serial.is_open:
            self.serial.close()

    def receive_loop(self) -> None:
        if not self.input_queue:
            return
        while not self.stopped:
            input_: bytes = self.serial.readline()
            print(f"RECEIVED: {input_}")
            self.input_queue.put(input_)

    def send_loop(self) -> None:
        if not self.output_queue:
            return
        while not self.stopped:
            try:
                output: bytes = self.output_queue.get(timeout=1)
            except queue.Empty:
                continue
            print(f"SENDING: {output}")
            self.serial.write(output)

    def close(self) -> None:
        self.stopped = True
        if self.serial and self.serial.is_open:
            self.serial.close()


class SimpleFreezeDripSerialListener(QObject):
    signal: Signal = Signal(str)


class SimpleFreezeDripSerial:
    def __init__(self, port_name: str, on_receive_listeners: Optional[list[SimpleFreezeDripSerialListener]] = None):
        self.port_name: str = port_name
        self.input_queue: Optional[queue.Queue] = queue.Queue()
        self.output_queue: Optional[queue.Queue] = queue.Queue()
        self.serial: Optional[FreezeDripSerial] = None
        self.stopped: bool = True
        self._on_receive_listeners: list[SimpleFreezeDripSerialListener] = list()
        if on_receive_listeners is not None:
            self._on_receive_listeners = on_receive_listeners

    def add_on_receive_listener(self, listener: SimpleFreezeDripSerialListener) -> None:
        self._on_receive_listeners.append(listener)

    def open(self) -> Optional['SimpleFreezeDripSerial']:
        self.stopped = False
        threading.Thread(target=self.receive_loop, daemon=True).start()
        try:
            self.serial = FreezeDripSerial(self.port_name, self.input_queue, self.output_queue)
        except serial.serialutil.SerialException:
            self.close()
            return
        return self

    def receive_loop(self) -> None:
        while not self.stopped:
            try:
                input_: str = self.input_queue.get(timeout=1).decode(errors='ignore').rstrip()
            except queue.Empty:
                continue
            listener: SimpleFreezeDripSerialListener
            for listener in self._on_receive_listeners:
                c: str
                listener.signal.emit(''.join(c for c in input_ if c.isprintable()))

    def send(self, output: str) -> 'SimpleFreezeDripSerial':
        output: bytes = f'{output}\r\n'.encode()
        self.output_queue.put(output)
        return self

    def close(self) -> 'SimpleFreezeDripSerial':
        self.stopped = True
        if self.serial:
            self.serial.close()
        return self

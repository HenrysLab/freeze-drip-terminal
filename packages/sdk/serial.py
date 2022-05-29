import dataclasses
import queue
import signal
import threading
from typing import Optional, Union

from PySide6.QtCore import QObject, Signal
import serial.tools.list_ports
import serial.tools.list_ports_common

from .data import Profile
from .util import floatable


@dataclasses.dataclass
class FreezeDripSerialResponse:
    response: str


@dataclasses.dataclass
class FreezeDripSerialData(Profile):
    status: Optional[str] = None
    temp: Optional[str] = None
    cd_battery_volt: Optional[str] = None
    rts_battery_volt: Optional[str] = None
    heartbeat_flag: Optional[str] = None
    low_temp_flag: Optional[str] = None
    low_bat_flag: Optional[str] = None
    setup_flag: Optional[str] = None


def get_available_serial_ports() -> list[serial.tools.list_ports_common.ListPortInfo]:
    return serial.tools.list_ports.comports()


class FreezeDripSerialParser:
    def __init__(self):
        self.status: str = ''

    def is_cd(self) -> Optional[bool]:
        if self.status:
            return bool(int(self.status, 16) & 0b1000_0000)

    def is_rts(self) -> Optional[bool]:
        if self.status:
            return not self.is_cd()

    def parse_line(self, line: str) -> Optional[Union[FreezeDripSerialData, FreezeDripSerialResponse]]:
        if line in ['OK', 'ERROR']:
            return FreezeDripSerialResponse(line)

        if line.startswith('Status : '):
            self.status = line.removeprefix('Status : ').removesuffix(' Hex')
            return FreezeDripSerialData(
                status=self.status,
                heartbeat_flag=str(bool(int(self.status, 16) & 0b1)),
                low_temp_flag=str(bool(int(self.status, 16) & 0b10)),
                low_bat_flag=str(bool(int(self.status, 16) & 0b100)),
                setup_flag=str(bool(int(self.status, 16) & 0b1_0000)))
        if line.startswith('Fahrenheit Temperature : '):
            return FreezeDripSerialData(
                temp=line.removeprefix('Fahrenheit Temperature : ').removesuffix(" 'F"))
        if line.startswith('Received Battery Value: '):
            if not self.is_cd():
                return
            return FreezeDripSerialData(
                rts_battery_volt=line.removeprefix('Received Battery Value: ').removesuffix(' Volts'))
        if line.startswith('Current Battery Voltage : '):
            if not self.status:
                return
            bat_volt: str = line.removeprefix('Current Battery Voltage : ').removesuffix(' Volts')
            if not floatable(bat_volt) or int(float(bat_volt) * 10) == 0xFF:
                return
            return FreezeDripSerialData(cd_battery_volt=bat_volt) if self.is_cd() \
                else FreezeDripSerialData(rts_battery_volt=bat_volt)

        if line.startswith('Temp. level 2 threshold : '):
            return FreezeDripSerialData(
                temp_lvl_2_thold=line.removeprefix('Temp. level 2 threshold : ').removesuffix(" 'F"))
        if line.startswith('Temp. level 3 threshold : '):
            return FreezeDripSerialData(
                temp_lvl_3_thold=line.removeprefix('Temp. level 3 threshold : ').removesuffix(" 'F"))
        if line.startswith('Temp. level 4 threshold : '):
            return FreezeDripSerialData(
                temp_lvl_4_thold=line.removeprefix('Temp. level 4 threshold : ').removesuffix(" 'F"))
        if line.startswith('Temperature sensitivity : '):
            return FreezeDripSerialData(
                temp_sensitivity=line.removeprefix('Temperature sensitivity : ').removesuffix(" 'F"))
        if line.startswith('Temp. detection interval : '):
            return FreezeDripSerialData(
                temp_detection_interval=line.removeprefix('Temp. detection interval : ').removesuffix(' Secs'))
        if line.startswith('Scale of S1 and S3 : '):
            return FreezeDripSerialData(
                scale_of_pump_on_time=line.removeprefix('Scale of S1 and S3 : ').removesuffix(' X'))
        if line.startswith('Pump on time of level 2 : '):
            return FreezeDripSerialData(
                lvl_2_pump_on_time=line.removeprefix('Pump on time of level 2 : ').removesuffix(' Secs'))
        if line.startswith('Pump off time of level 2 : '):
            return FreezeDripSerialData(
                lvl_2_pump_off_time=line.removeprefix('Pump off time of level 2 : ').removesuffix(' Secs'))
        if line.startswith('Pump on time of level 3 : '):
            return FreezeDripSerialData(
                lvl_3_pump_on_time=line.removeprefix('Pump on time of level 3 : ').removesuffix(' Secs'))
        if line.startswith('Pump off time of level 3 : '):
            return FreezeDripSerialData(
                lvl_3_pump_off_time=line.removeprefix('Pump off time of level 3 : ').removesuffix(' Secs'))
        if line.startswith('Low Battery threshold : '):
            return FreezeDripSerialData(
                low_battery_thold=line.removeprefix('Low Battery threshold : ').removesuffix(' Volts'))
        if line.startswith('Interval of the Lost alarm : '):
            return FreezeDripSerialData(
                lost_alarm_interval=line.removeprefix('Interval of the Lost alarm : ').removesuffix(' Secs'))
        if line.startswith('H.B./L. Bat. interval : '):
            return FreezeDripSerialData(
                heartbeat_interval=line.removeprefix('H.B./L. Bat. interval : ').removesuffix(' Mins'))
        if line.startswith('Setup signal interval : '):
            return FreezeDripSerialData(
                setup_duration=line.removeprefix('Setup signal interval : ').removesuffix(' Mins'))

    def parse_profile(self, profile: Profile) -> str:
        profile_str: str = '#'
        profile_str += 'B' + ',' + f"{int(float(profile.low_battery_thold)*10):02X}" + ','
        profile_str += 'RBV' + ',' + 'FF' + ','
        profile_str += 'CBV' + ',' + 'FF' + ','
        profile_str += 'S' + ',' + f"{int(profile.setup_duration):02X}" + ','
        profile_str += 'H' + ',' + f"{int(profile.heartbeat_interval):02X}" + ','
        profile_str += 'T' + ',' + f"{int(float(profile.temp_sensitivity)*10):02X}" + ','
        profile_str += 'U' + ',' + f"{int(float(profile.scale_of_pump_on_time)*10):02X}" + ','
        profile_str += 'L' + ',' + f"{int(profile.lost_alarm_interval):04X}" + ','
        profile_str += 'D' + ',' + f"{int(profile.temp_detection_interval):04X}" + ','
        profile_str += 'T1' + ',' + f"{int(float(profile.temp_lvl_2_thold)*10):04X}" + ','
        profile_str += 'T2' + ',' + f"{int(float(profile.temp_lvl_3_thold)*10):04X}" + ','
        profile_str += 'T3' + ',' + f"{int(float(profile.temp_lvl_4_thold)*10):04X}" + ','
        profile_str += 'S1' + ',' + f"{int(profile.lvl_2_pump_on_time):04X}" + ','
        profile_str += 'S2' + ',' + f"{int(profile.lvl_2_pump_off_time):04X}" + ','
        profile_str += 'S3' + ',' + f"{int(profile.lvl_3_pump_on_time):04X}" + ','
        profile_str += 'S4' + ',' + f"{int(profile.lvl_3_pump_off_time):04X}"
        profile_str += '$'
        return profile_str


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
                input_: str = self.input_queue.get(timeout=1).decode(errors='ignore').strip()
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

from __future__ import annotations

import datetime
import importlib.resources
import pathlib
import time
from typing import Optional, Union

import PySide6.QtXml  # This is only for PyInstaller to process properly
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QListWidgetItem,
    QMainWindow)
import sdk
import serial.tools.list_ports
import serial.tools.list_ports_common

from .popup_hookable_combox import QPopupHookableComboBox
from .. import ui_model


class QMainWindowExt(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_window_model: ui_model.MainWindowModel = ui_model.MainWindowModel()

        self.serial: Optional[sdk.SimpleFreezeDripSerial] = None
        self.seirla_receiver: sdk.SimpleFreezeDripSerialListener = sdk.SimpleFreezeDripSerialListener()
        self.seirla_receiver.signal.connect(self.on_receive_serial_line)
        self.serial_parser: sdk.FreezeDripSerialParser = sdk.FreezeDripSerialParser()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.serial:
            self.serial.close()
        super().closeEvent(event)

    def setup(self) -> None:
        self.setWindowTitle(f"{self.windowTitle()} {sdk.VERSION}")

        app_icon: pathlib.Path
        with importlib.resources.path(__package__, 'main_window.ico') as app_icon:
            self.setWindowIcon(QIcon(str(app_icon)))

        self.move(QApplication.primaryScreen().availableGeometry().center() - self.rect().center())

        self.main_window_model.add_on_changed_observer(self.on_connected_changed, 'connected')
        self.port_popup_hookable_combo_box.add_on_show_popup_listener(self.on_popup_combo_box)
        self.port_connect_push_button.clicked.connect(self.on_port_connect_push_button_clicked)
        self.port_disconnect_push_button.clicked.connect(self.on_port_disconnect_push_button_clicked)

        self.refresh_push_button.clicked.connect(self.on_refresh_push_button_clicked)

        self.main_window_model.add_on_profiles_changed_listener(self.on_profiles_model_changed)
        self.profile_list_widget.currentItemChanged.connect(self.on_profile_list_widget_current_item_changed)

        self.remove_profile_push_button.clicked.connect(self.on_remove_profile_push_button_clicked)
        self.add_profile_push_button.clicked.connect(self.on_add_profile_push_button_clicked)

        self.main_window_model.add_on_changed_observer(self.on_profile_model_changed, 'profile')
        self.profile_name_line_edit.textChanged.connect(self.on_profile_name_line_edit_text_changed)
        self.expected_temp_lvl_2_thold_line_edit.textChanged.connect(
            self.on_expected_temp_lvl_2_thold_line_edit_text_changed)
        self.expected_temp_lvl_3_thold_line_edit.textChanged.connect(
            self.on_expected_temp_lvl_3_thold_line_edit_text_changed)
        self.expected_temp_lvl_4_thold_line_edit.textChanged.connect(
            self.on_expected_temp_lvl_4_thold_line_edit_text_changed)
        self.expected_temp_sensitivity_line_edit.textChanged.connect(
            self.on_expected_temp_sensitivity_line_edit_text_changed)
        self.expected_temp_detection_interval_line_edit.textChanged.connect(
            self.on_expected_temp_detection_interval_line_edit_text_changed)
        self.expected_scale_of_pump_on_time_line_edit.textChanged.connect(
            self.on_expected_scale_of_pump_on_time_line_edit_text_changed)
        self.expected_lvl_2_pump_on_time_line_edit.textChanged.connect(
            self.on_expected_lvl_2_pump_on_time_line_edit_text_changed)
        self.expected_lvl_2_pump_off_time_line_edit.textChanged.connect(
            self.on_expected_lvl_2_pump_off_time_line_edit_text_changed)
        self.expected_lvl_3_pump_on_time_line_edit.textChanged.connect(
            self.on_expected_lvl_3_pump_on_time_line_edit_text_changed)
        self.expected_lvl_3_pump_off_time_line_edit.textChanged.connect(
            self.on_expected_lvl_3_pump_off_time_line_edit_text_changed)
        self.expected_low_battery_thold_line_edit.textChanged.connect(
            self.on_expected_low_battery_thold_line_edit_text_changed)
        self.expected_lost_alarm_interval_line_edit.textChanged.connect(
            self.on_expected_lost_alarm_interval_line_edit_text_changed)
        self.expected_heartbeat_interval_line_edit.textChanged.connect(
            self.on_expected_heartbeat_interval_line_edit_text_changed)
        self.expected_setup_duration_line_edit.textChanged.connect(
            self.on_expected_setup_duration_line_edit_text_changed)

        self.send_profile_push_button.clicked.connect(self.on_send_profile_push_button_clicked)
        self.save_profile_push_button.clicked.connect(self.on_save_profile_push_button_clicked)

        self.main_window_model.add_on_commands_changed_listener(self.on_commands_model_changed)
        self.command_list_widget.currentItemChanged.connect(self.on_command_list_widget_current_item_changed)

        self.main_window_model.add_on_changed_observer(self.on_command_model_changed, 'command')
        self.command_name_line_edit.textChanged.connect(
            lambda x: setattr(self.main_window_model.command, 'name', x))
        self.command_line_edit.textChanged.connect(
            lambda x: setattr(self.main_window_model.command, 'command', x))

        self.remove_command_push_button.clicked.connect(self.on_remove_command_push_button_clicked)
        self.add_command_push_button.clicked.connect(self.on_add_command_push_button_clicked)
        self.save_command_push_button.clicked.connect(self.on_save_command_push_button_clicked)
        self.send_command_push_button.clicked.connect(self.on_send_command_push_button_clicked)

        self.terminal_plain_text_edit.textChanged.connect(self.on_terminal_plain_text_edit_text_changed)
        self.clear_terminal_push_button.clicked.connect(self.on_clear_terminal_push_button_clicked)

        self.update_port_popup_hookable_combo_box()
        self.on_connected_changed(False)

        self.on_profiles_model_changed(self.main_window_model.profiles)
        self.on_commands_model_changed(self.main_window_model.commands)

        self.port_popup_hookable_combo_box.setFocus()

    def show(self) -> None:
        self.setup()
        super().show()

    def update_port_popup_hookable_combo_box(self):
        origin: str = self.port_popup_hookable_combo_box.currentText()
        self.port_popup_hookable_combo_box.clear()
        port_infos: list[serial.tools.list_ports_common.ListPortInfo] = sdk.get_available_serial_ports()
        port_info: serial.tools.list_ports_common.ListPortInfo
        port_name: str
        self.port_popup_hookable_combo_box.addItems(sorted(port_info.name for port_info in port_infos))
        index: int = self.port_popup_hookable_combo_box.findText(origin, flags=Qt.MatchExactly)
        self.port_popup_hookable_combo_box.setCurrentIndex(0 if index < 0 else index)

    def on_popup_combo_box(self, combo_box: QPopupHookableComboBox):
        self.update_port_popup_hookable_combo_box()

    def on_connected_changed(self, connected: bool):
        self.port_popup_hookable_combo_box.setEnabled(not connected)
        self.port_connect_push_button.setEnabled(
            sdk.get_available_serial_ports() and not connected)
        self.port_disconnect_push_button.setEnabled(connected)
        self.refresh_push_button.setEnabled(connected)
        self.send_profile_push_button.setEnabled(connected)
        self.send_command_push_button.setEnabled(connected)
        self.update_port_popup_hookable_combo_box()

        self.status_code_line_edit.setEnabled(connected)
        self.temp_line_edit.setEnabled(connected)
        self.rts_bat_volt_line_edit.setEnabled(connected)
        self.cd_bat_volt_line_edit.setEnabled(connected)
        self.heartbeat_flag_line_edit.setEnabled(connected)
        self.low_temp_flag_line_edit.setEnabled(connected)
        self.low_bat_flag_line_edit.setEnabled(connected)
        self.setup_flag_line_edit.setEnabled(connected)

        self.updated_at_line_edit.setEnabled(connected)
        self.current_temp_lvl_2_thold_line_edit.setEnabled(connected)
        self.current_temp_lvl_3_thold_line_edit.setEnabled(connected)
        self.current_temp_lvl_4_thold_line_edit.setEnabled(connected)
        self.current_temp_sensitivity_line_edit.setEnabled(connected)
        self.current_temp_detection_interval_line_edit.setEnabled(connected)
        self.current_scale_of_pump_on_time_line_edit.setEnabled(connected)
        self.current_lvl_2_pump_on_time_line_edit.setEnabled(connected)
        self.current_lvl_2_pump_off_time_line_edit.setEnabled(connected)
        self.current_lvl_3_pump_on_time_line_edit.setEnabled(connected)
        self.current_lvl_3_pump_off_time_line_edit.setEnabled(connected)
        self.current_low_battery_thold_line_edit.setEnabled(connected)
        self.current_lost_alarm_interval_line_edit.setEnabled(connected)
        self.current_heartbeat_interval_line_edit.setEnabled(connected)
        self.current_setup_duration_line_edit.setEnabled(connected)

        self.terminal_plain_text_edit.setEnabled(connected)

        if connected:
            self.serial = sdk.SimpleFreezeDripSerial(
                self.port_popup_hookable_combo_box.currentText(),
                [self.seirla_receiver]).open()
            if not self.serial:
                self.on_connected_changed(False)
        elif self.serial:
            self.serial.close()

    def on_port_connect_push_button_clicked(self):
        self.main_window_model.connected = True

    def on_port_disconnect_push_button_clicked(self):
        self.main_window_model.connected = False

    def on_refresh_push_button_clicked(self):
        self.status_code_line_edit.setText("")
        self.current_low_battery_thold_line_edit.setText("")
        self.cd_bat_volt_line_edit.setText("")
        self.rts_bat_volt_line_edit.setText("")
        self.heartbeat_flag_line_edit.setText("")
        self.low_temp_flag_line_edit.setText("")
        self.low_bat_flag_line_edit.setText("")
        self.setup_flag_line_edit.setText("")

        self.updated_at_line_edit.setText("")
        self.current_temp_lvl_2_thold_line_edit.setText("")
        self.current_temp_lvl_3_thold_line_edit.setText("")
        self.current_temp_lvl_4_thold_line_edit.setText("")
        self.current_temp_sensitivity_line_edit.setText("")
        self.current_temp_detection_interval_line_edit.setText("")
        self.current_scale_of_pump_on_time_line_edit.setText("")
        self.current_lvl_2_pump_on_time_line_edit.setText("")
        self.current_lvl_2_pump_off_time_line_edit.setText("")
        self.current_lvl_3_pump_on_time_line_edit.setText("")
        self.current_lvl_3_pump_off_time_line_edit.setText("")
        self.current_low_battery_thold_line_edit.setText("")
        self.current_lost_alarm_interval_line_edit.setText("")
        self.current_heartbeat_interval_line_edit.setText("")
        self.current_setup_duration_line_edit.setText("")

        if self.serial:
            self.serial.send('RD')
            time.sleep(0.1)
            self.serial.send('CD0')

    def on_remove_profile_push_button_clicked(self):
        self.main_window_model.remove_profile()

    def on_add_profile_push_button_clicked(self):
        self.main_window_model.create_profile()
        self.profile_list_widget.setCurrentRow(self.profile_list_widget.count() - 1)

    def on_send_profile_push_button_clicked(self):
        if self.serial:
            self.serial.send(self.serial_parser.parse_profile(self.main_window_model.profile))
            time.sleep(0.1)
            self.serial.send('CD0')

    def on_save_profile_push_button_clicked(self):
        self.main_window_model.save_profile()

    def on_profiles_model_changed(self, profiles: list[sdk.Profile]) -> None:
        last_index: int = self.profile_list_widget.currentRow()
        self.profile_list_widget.clear()
        profile: sdk.Profile
        self.profile_list_widget.addItems(profile.name for profile in profiles)
        self.profile_list_widget.setCurrentRow(
            last_index if 0 <= last_index < self.profile_list_widget.count() else self.profile_list_widget.count() - 1)

    def on_profile_list_widget_current_item_changed(
            self, selected: QListWidgetItem, deselected: QListWidgetItem) -> None:
        if self.profile_list_widget.currentRow() >= 0:
            self.main_window_model.profile = self.main_window_model.profiles[self.profile_list_widget.currentRow()]

    def on_profile_model_changed(self, profile: Optional[sdk.Profile]) -> None:
        if not profile:
            return
        self.profile_name_line_edit.setText(profile.name)
        self.expected_temp_lvl_2_thold_line_edit.setText(profile.temp_lvl_2_thold)
        self.expected_temp_lvl_3_thold_line_edit.setText(profile.temp_lvl_3_thold)
        self.expected_temp_lvl_4_thold_line_edit.setText(profile.temp_lvl_4_thold)
        self.expected_temp_sensitivity_line_edit.setText(profile.temp_sensitivity)
        self.expected_temp_detection_interval_line_edit.setText(profile.temp_detection_interval)
        self.expected_scale_of_pump_on_time_line_edit.setText(profile.scale_of_pump_on_time)
        self.expected_lvl_2_pump_on_time_line_edit.setText(profile.lvl_2_pump_on_time)
        self.expected_lvl_2_pump_off_time_line_edit.setText(profile.lvl_2_pump_off_time)
        self.expected_lvl_3_pump_on_time_line_edit.setText(profile.lvl_3_pump_on_time)
        self.expected_lvl_3_pump_off_time_line_edit.setText(profile.lvl_3_pump_off_time)
        self.expected_low_battery_thold_line_edit.setText(profile.low_battery_thold)
        self.expected_lost_alarm_interval_line_edit.setText(profile.lost_alarm_interval)
        self.expected_heartbeat_interval_line_edit.setText(profile.heartbeat_interval)
        self.expected_setup_duration_line_edit.setText(profile.setup_duration)

    def on_remove_command_push_button_clicked(self):
        self.main_window_model.remove_command()

    def on_add_command_push_button_clicked(self):
        self.main_window_model.create_command()
        self.command_list_widget.setCurrentRow(self.command_list_widget.count() - 1)

    def on_save_command_push_button_clicked(self):
        self.main_window_model.save_command()

    def on_send_command_push_button_clicked(self):
        if self.serial:
            self.serial.send(self.command_line_edit.text())

    def on_terminal_plain_text_edit_text_changed(self):
        self.clear_terminal_push_button.setEnabled(bool(self.terminal_plain_text_edit.toPlainText()))

    def on_clear_terminal_push_button_clicked(self):
        self.terminal_plain_text_edit.setPlainText("")

    def on_profile_name_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.name = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_temp_lvl_2_thold_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.temp_lvl_2_thold = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_temp_lvl_3_thold_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.temp_lvl_3_thold = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_temp_lvl_4_thold_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.temp_lvl_4_thold = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_temp_sensitivity_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.temp_sensitivity = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_temp_detection_interval_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.temp_detection_interval = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_scale_of_pump_on_time_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.scale_of_pump_on_time = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_lvl_2_pump_on_time_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.lvl_2_pump_on_time = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_lvl_2_pump_off_time_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.lvl_2_pump_off_time = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_lvl_3_pump_on_time_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.lvl_3_pump_on_time = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_lvl_3_pump_off_time_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.lvl_3_pump_off_time = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_low_battery_thold_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.low_battery_thold = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_lost_alarm_interval_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.lost_alarm_interval = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_heartbeat_interval_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.heartbeat_interval = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_expected_setup_duration_line_edit_text_changed(self, changed_text: str):
        self.main_window_model.profile.setup_duration = changed_text
        self.save_profile_push_button.setEnabled(self.main_window_model.is_profile_valid())
        self.send_profile_push_button.setEnabled(
            self.main_window_model.is_profile_valid() and self.main_window_model.connected)

    def on_commands_model_changed(self, commands: list[sdk.Command]) -> None:
        last_index: int = self.command_list_widget.currentRow()
        self.command_list_widget.clear()
        command: sdk.Command
        self.command_list_widget.addItems(command.name for command in commands)
        self.command_list_widget.setCurrentRow(
            last_index if 0 <= last_index < self.command_list_widget.count() else self.command_list_widget.count() - 1)

    def on_command_list_widget_current_item_changed(
            self, selected: QListWidgetItem, deselected: QListWidgetItem) -> None:
        if self.command_list_widget.currentRow() >= 0:
            self.main_window_model.command = self.main_window_model.commands[self.command_list_widget.currentRow()]

    def on_command_model_changed(self, command: Optional[sdk.Command]) -> None:
        if not command:
            return
        self.command_name_line_edit.setText(command.name)
        self.command_line_edit.setText(command.command)

    def on_receive_serial_line(self, line: str):
        self.terminal_plain_text_edit.moveCursor(QTextCursor.End)
        self.terminal_plain_text_edit.insertPlainText(f"{line}\n")
        self.terminal_plain_text_edit.moveCursor(QTextCursor.End)

        data: Optional[Union[sdk.FreezeDripSerialData, sdk.FreezeDripSerialResponse]] = \
            self.serial_parser.parse_line(line)

        if isinstance(data, sdk.FreezeDripSerialData):
            if data.status:
                self.status_code_line_edit.setText(data.status)
            if data.temp:
                self.temp_line_edit.setText(str(float(data.temp)))
            if data.rts_battery_volt:
                self.rts_bat_volt_line_edit.setText(data.rts_battery_volt)
            if data.cd_battery_volt:
                self.cd_bat_volt_line_edit.setText(data.cd_battery_volt)
            if data.heartbeat_flag:
                self.heartbeat_flag_line_edit.setText(data.heartbeat_flag)
            if data.low_temp_flag:
                self.low_temp_flag_line_edit.setText(data.low_temp_flag)
            if data.low_bat_flag:
                self.low_bat_flag_line_edit.setText(data.low_bat_flag)
            if data.setup_flag:
                self.setup_flag_line_edit.setText(data.setup_flag)
            if data.temp_lvl_2_thold:
                self.current_temp_lvl_2_thold_line_edit.setText(str(float(data.temp_lvl_2_thold)))
            if data.temp_lvl_3_thold:
                self.current_temp_lvl_3_thold_line_edit.setText(str(float(data.temp_lvl_3_thold)))
            if data.temp_lvl_4_thold:
                self.current_temp_lvl_4_thold_line_edit.setText(str(float(data.temp_lvl_4_thold)))
            if data.temp_sensitivity:
                self.current_temp_sensitivity_line_edit.setText(str(float(data.temp_sensitivity)))
            if data.temp_detection_interval:
                self.current_temp_detection_interval_line_edit.setText(str(int(data.temp_detection_interval)))
            if data.scale_of_pump_on_time:
                self.current_scale_of_pump_on_time_line_edit.setText(str(float(data.scale_of_pump_on_time)))
            if data.lvl_2_pump_on_time:
                self.current_lvl_2_pump_on_time_line_edit.setText(str(int(data.lvl_2_pump_on_time)))
            if data.lvl_2_pump_off_time:
                self.current_lvl_2_pump_off_time_line_edit.setText(str(int(data.lvl_2_pump_off_time)))
            if data.lvl_3_pump_on_time:
                self.current_lvl_3_pump_on_time_line_edit.setText(str(int(data.lvl_3_pump_on_time)))
            if data.lvl_3_pump_off_time:
                self.current_lvl_3_pump_off_time_line_edit.setText(str(int(data.lvl_3_pump_off_time)))
            if data.low_battery_thold:
                self.current_low_battery_thold_line_edit.setText(str(float(data.low_battery_thold)))
            if data.lost_alarm_interval:
                self.current_lost_alarm_interval_line_edit.setText(str(int(data.lost_alarm_interval)))
            if data.heartbeat_interval:
                self.current_heartbeat_interval_line_edit.setText(str(int(data.heartbeat_interval)))
            if data.setup_duration:
                self.current_setup_duration_line_edit.setText(str(int(data.setup_duration)))
            self.updated_at_line_edit.setText(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

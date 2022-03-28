from __future__ import annotations

import importlib.resources
import pathlib
from typing import Optional

import sdk
import PySide6.QtXml  # This is only for PyInstaller to process properly
from PySide6.QtCore import QIODevice, QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QPushButton)

from .ui import UI
from .. import ui_model


class MainWindow(UI, sdk.Singleton):
    def __init__(self):
        super().__init__(parent=None)
        self.main_window: Optional[QMainWindow] = None
        self.main_window_model: Optional[ui_model.MainWindowModel] = None

        self.port_combo_box: Optional[QComboBox] = None
        self.port_connect_push_button: Optional[QPushButton] = None
        self.port_disconnect_push_button: Optional[QPushButton] = None

        self.refresh_push_button: Optional[QPushButton] = None

        self.updated_at_line_edit: Optional[QLineEdit] = None
        self.current_temp_lvl_2_thold_line_edit: Optional[QLineEdit] = None
        self.current_temp_lvl_3_thold_line_edit: Optional[QLineEdit] = None
        self.current_temp_lvl_4_thold_line_edit: Optional[QLineEdit] = None
        self.current_temp_sensitivity_line_edit: Optional[QLineEdit] = None
        self.current_temp_detection_interval_line_edit: Optional[QLineEdit] = None
        self.current_scale_of_pump_on_time_line_edit: Optional[QLineEdit] = None
        self.current_lvl_2_pump_on_time_line_edit: Optional[QLineEdit] = None
        self.current_lvl_2_pump_off_time_line_edit: Optional[QLineEdit] = None
        self.current_lvl_3_pump_on_time_line_edit: Optional[QLineEdit] = None
        self.current_lvl_3_pump_off_time_line_edit: Optional[QLineEdit] = None
        self.current_low_battery_thold_line_edit: Optional[QLineEdit] = None
        self.current_lost_alarm_interval_line_edit: Optional[QLineEdit] = None
        self.current_heartbeat_interval_line_edit: Optional[QLineEdit] = None
        self.current_setup_duration_line_edit: Optional[QLineEdit] = None

        self.temp_line_edit: Optional[QLineEdit] = None
        self.rts_bat_volt_line_edit: Optional[QLineEdit] = None
        self.cd_bat_volt_line_edit: Optional[QLineEdit] = None
        self.heartbeat_flag_line_edit: Optional[QLineEdit] = None
        self.low_temp_flag_line_edit: Optional[QLineEdit] = None
        self.low_bat_flag_line_edit: Optional[QLineEdit] = None
        self.setup_flag_line_edit: Optional[QLineEdit] = None

        self.profile_list_widget: Optional[QListWidget] = None
        self.add_profile_push_button: Optional[QPushButton] = None
        self.remove_profile_push_button: Optional[QPushButton] = None

        self.profile_name_line_edit: Optional[QLineEdit] = None
        self.expected_temp_lvl_2_thold_line_edit: Optional[QLineEdit] = None
        self.expected_temp_lvl_3_thold_line_edit: Optional[QLineEdit] = None
        self.expected_temp_lvl_4_thold_line_edit: Optional[QLineEdit] = None
        self.expected_temp_sensitivity_line_edit: Optional[QLineEdit] = None
        self.expected_temp_detection_interval_line_edit: Optional[QLineEdit] = None
        self.expected_scale_of_pump_on_time_line_edit: Optional[QLineEdit] = None
        self.expected_lvl_2_pump_on_time_line_edit: Optional[QLineEdit] = None
        self.expected_lvl_2_pump_off_time_line_edit: Optional[QLineEdit] = None
        self.expected_lvl_3_pump_on_time_line_edit: Optional[QLineEdit] = None
        self.expected_lvl_3_pump_off_time_line_edit: Optional[QLineEdit] = None
        self.expected_low_battery_thold_line_edit: Optional[QLineEdit] = None
        self.expected_lost_alarm_interval_line_edit: Optional[QLineEdit] = None
        self.expected_heartbeat_interval_line_edit: Optional[QLineEdit] = None
        self.expected_setup_duration_line_edit: Optional[QLineEdit] = None

        self.send_profile_push_button: Optional[QPushButton] = None
        self.save_profile_push_button: Optional[QPushButton] = None

        self.command_list_widget: Optional[QListWidget] = None
        self.add_command_push_button: Optional[QPushButton] = None
        self.remove_command_push_button: Optional[QPushButton] = None

        self.command_name_line_edit: Optional[QLineEdit] = None
        self.save_command_push_button: Optional[QPushButton] = None
        self.command_plain_text_edit: Optional[QPlainTextEdit] = None
        self.send_command_push_button: Optional[QPushButton] = None
        self.terminal_plain_text_edit: Optional[QPlainTextEdit] = None
        self.clear_terminal_push_button: Optional[QPushButton] = None

    def bind(self, main_window_model: ui_model.MainWindowModel) -> MainWindow:
        super().bind(main_window_model)
        self.main_window_model = main_window_model

        main_window_model.add_on_profiles_changed_listener(self.on_profiles_model_changed)
        self.profile_list_widget.currentItemChanged.connect(self.on_profile_list_widget_current_item_changed)

        self.remove_profile_push_button.clicked.connect(self.on_remove_profile_push_button_clicked)
        self.add_profile_push_button.clicked.connect(self.on_add_profile_push_button_clicked)

        main_window_model.add_on_changed_observer(self.on_profile_model_changed, 'profile')
        self.profile_name_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'name', x))
        self.expected_temp_lvl_2_thold_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'temp_lvl_2_thold', x))
        self.expected_temp_lvl_3_thold_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'temp_lvl_3_thold', x))
        self.expected_temp_lvl_4_thold_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'temp_lvl_4_thold', x))
        self.expected_temp_sensitivity_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'temp_sensitivity', x))
        self.expected_temp_detection_interval_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'temp_detection_interval', x))
        self.expected_scale_of_pump_on_time_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'scale_of_pump_on_time', x))
        self.expected_lvl_2_pump_on_time_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'lvl_2_pump_on_time', x))
        self.expected_lvl_2_pump_off_time_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'lvl_2_pump_off_time', x))
        self.expected_lvl_3_pump_on_time_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'lvl_3_pump_on_time', x))
        self.expected_lvl_3_pump_off_time_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'lvl_3_pump_off_time', x))
        self.expected_low_battery_thold_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'low_battery_thold', x))
        self.expected_lost_alarm_interval_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'lost_alarm_interval', x))
        self.expected_heartbeat_interval_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'heartbeat_interval', x))
        self.expected_setup_duration_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.profile, 'setup_duration', x))

        self.save_profile_push_button.clicked.connect(self.on_save_profile_push_button_clicked)

        main_window_model.add_on_commands_changed_listener(self.on_commands_model_changed)
        self.command_list_widget.currentItemChanged.connect(self.on_command_list_widget_current_item_changed)

        self.remove_command_push_button.clicked.connect(self.on_remove_command_push_button_clicked)
        self.add_command_push_button.clicked.connect(self.on_add_command_push_button_clicked)

        main_window_model.add_on_changed_observer(self.on_command_model_changed, 'command')
        self.command_name_line_edit.textChanged.connect(
            lambda x: setattr(main_window_model.command, 'name', x))
        self.command_plain_text_edit.textChanged.connect(
            lambda: setattr(main_window_model.command, 'command', self.command_plain_text_edit.toPlainText()))

        self.save_command_push_button.clicked.connect(self.on_save_command_push_button_clicked)
        return self

    def inflate(self, ui_path: Optional[pathlib.Path] = None) -> MainWindow:
        super().inflate(ui_path)
        main_window_ui: pathlib.Path
        with importlib.resources.path(__package__, 'main_window.ui') as main_window_ui:
            main_window_ui_qfile: QFile = QFile(str(main_window_ui))
            if not main_window_ui_qfile.open(QIODevice.ReadOnly):
                raise RuntimeError(f"Cannot open {main_window_ui}: {main_window_ui_qfile.errorString()}")
            qui_loader: QUiLoader = QUiLoader()
            self.main_window = qui_loader.load(main_window_ui_qfile)
            main_window_ui_qfile.close()
            if not self.main_window:
                raise RuntimeError(qui_loader.errorString())

        self.port_combo_box = getattr(self.main_window, 'comboBox')
        self.port_combo_box.setFocus()
        self.port_connect_push_button = getattr(self.main_window, 'pushButton_3')
        self.port_disconnect_push_button = getattr(self.main_window, 'pushButton_4')

        self.refresh_push_button = getattr(self.main_window, 'pushButton_5')

        self.updated_at_line_edit = getattr(self.main_window, 'lineEdit_25')
        self.current_temp_lvl_2_thold_line_edit = getattr(self.main_window, 'lineEdit_17')
        self.current_temp_lvl_3_thold_line_edit = getattr(self.main_window, 'lineEdit_28')
        self.current_temp_lvl_4_thold_line_edit = getattr(self.main_window, 'lineEdit_20')
        self.current_temp_sensitivity_line_edit = getattr(self.main_window, 'lineEdit_18')
        self.current_temp_detection_interval_line_edit = getattr(self.main_window, 'lineEdit_19')
        self.current_scale_of_pump_on_time_line_edit = getattr(self.main_window, 'lineEdit_22')
        self.current_lvl_2_pump_on_time_line_edit = getattr(self.main_window, 'lineEdit_27')
        self.current_lvl_2_pump_off_time_line_edit = getattr(self.main_window, 'lineEdit_26')
        self.current_lvl_3_pump_on_time_line_edit = getattr(self.main_window, 'lineEdit_24')
        self.current_lvl_3_pump_off_time_line_edit = getattr(self.main_window, 'lineEdit_21')
        self.current_low_battery_thold_line_edit = getattr(self.main_window, 'lineEdit_29')
        self.current_lost_alarm_interval_line_edit = getattr(self.main_window, 'lineEdit_30')
        self.current_heartbeat_interval_line_edit = getattr(self.main_window, 'lineEdit_31')
        self.current_setup_duration_line_edit = getattr(self.main_window, 'lineEdit_32')

        self.temp_line_edit = getattr(self.main_window, 'lineEdit_39')
        self.rts_bat_volt_line_edit = getattr(self.main_window, 'lineEdit_5')
        self.cd_bat_volt_line_edit = getattr(self.main_window, 'lineEdit_23')
        self.heartbeat_flag_line_edit = getattr(self.main_window, 'lineEdit_33')
        self.low_temp_flag_line_edit = getattr(self.main_window, 'lineEdit_36')
        self.low_bat_flag_line_edit = getattr(self.main_window, 'lineEdit_34')
        self.setup_flag_line_edit = getattr(self.main_window, 'lineEdit_37')

        self.profile_list_widget = getattr(self.main_window, 'listWidget')
        self.remove_profile_push_button = getattr(self.main_window, 'pushButton')
        self.add_profile_push_button = getattr(self.main_window, 'pushButton_2')

        self.profile_name_line_edit = getattr(self.main_window, 'lineEdit')
        self.expected_temp_lvl_2_thold_line_edit = getattr(self.main_window, 'lineEdit_2')
        self.expected_temp_lvl_3_thold_line_edit = getattr(self.main_window, 'lineEdit_3')
        self.expected_temp_lvl_4_thold_line_edit = getattr(self.main_window, 'lineEdit_4')
        self.expected_temp_sensitivity_line_edit = getattr(self.main_window, 'lineEdit_6')
        self.expected_temp_detection_interval_line_edit = getattr(self.main_window, 'lineEdit_7')
        self.expected_scale_of_pump_on_time_line_edit = getattr(self.main_window, 'lineEdit_8')
        self.expected_lvl_2_pump_on_time_line_edit = getattr(self.main_window, 'lineEdit_9')
        self.expected_lvl_2_pump_off_time_line_edit = getattr(self.main_window, 'lineEdit_10')
        self.expected_lvl_3_pump_on_time_line_edit = getattr(self.main_window, 'lineEdit_11')
        self.expected_lvl_3_pump_off_time_line_edit = getattr(self.main_window, 'lineEdit_12')
        self.expected_low_battery_thold_line_edit = getattr(self.main_window, 'lineEdit_13')
        self.expected_lost_alarm_interval_line_edit = getattr(self.main_window, 'lineEdit_14')
        self.expected_heartbeat_interval_line_edit = getattr(self.main_window, 'lineEdit_15')
        self.expected_setup_duration_line_edit = getattr(self.main_window, 'lineEdit_16')

        self.send_profile_push_button = getattr(self.main_window, 'pushButton_6')
        self.save_profile_push_button = getattr(self.main_window, 'pushButton_7')

        self.command_list_widget = getattr(self.main_window, 'listWidget_2')
        self.remove_command_push_button = getattr(self.main_window, 'pushButton_11')
        self.add_command_push_button = getattr(self.main_window, 'pushButton_10')

        self.command_name_line_edit = getattr(self.main_window, 'lineEdit_35')
        self.save_command_push_button = getattr(self.main_window, 'pushButton_9')
        self.command_plain_text_edit = getattr(self.main_window, 'plainTextEdit')
        self.send_command_push_button = getattr(self.main_window, 'pushButton_8')
        self.terminal_plain_text_edit = getattr(self.main_window, 'plainTextEdit_2')
        self.clear_terminal_push_button = getattr(self.main_window, 'pushButton_13')
        return self

    def show(self) -> MainWindow:
        super().show()

        self.on_profiles_model_changed(self.main_window_model.profiles)
        self.on_commands_model_changed(self.main_window_model.commands)

        self.main_window.show()
        return self

    def on_remove_profile_push_button_clicked(self):
        self.main_window_model.remove_profile()

    def on_add_profile_push_button_clicked(self):
        self.main_window_model.create_profile()
        self.profile_list_widget.setCurrentRow(self.profile_list_widget.count() - 1)

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
        self.command_plain_text_edit.setPlainText(command.command)

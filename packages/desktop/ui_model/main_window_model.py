import pathlib
from typing import Callable, Optional

import sdk
from .ui_model import UIModel


class MainWindowModel(UIModel):
    def __init__(self):
        super().__init__()

        self._connected: bool = False

        self.profile_db: sdk.ProfileDatabase = sdk.ProfileDatabase(pathlib.Path('freeze-drip-terminal-desktop.db'))
        self._profile: Optional[sdk.Profile] = None
        self._profiles_changed_listeners: list[Callable[[list[sdk.Profile]], None]] = list()

        self.command_db: sdk.CommandDatabase = sdk.CommandDatabase(pathlib.Path('freeze-drip-terminal-desktop.db'))
        self._command: Optional[sdk.Command] = None
        self._commands_changed_listeners: list[Callable[[list[sdk.Command]], None]] = list()

    @property
    def connected(self) -> bool:
        return self._connected

    @connected.setter
    def connected(self, value: bool) -> None:
        self._connected = value

    def add_on_profiles_changed_listener(self, listener: Callable[[list[sdk.Profile]], None]) -> None:
        self._profiles_changed_listeners.append(listener)

    def notify_profiles_changed(self) -> None:
        profiles = self.profiles
        listener: Callable[[list[sdk.Profile]], None]
        for listener in self._profiles_changed_listeners:
            listener(profiles)

    def fill_profile(self, id_: int):
        self.profile = self.profile_db.get(id_)

    def generate_default_profiles(self):
        self.profile_db.add(sdk.Profile(
            name="Default",
            temp_lvl_2_thold="40",
            temp_lvl_3_thold="37",
            temp_lvl_4_thold="32",
            temp_sensitivity="1",
            temp_detection_interval="60",
            scale_of_pump_on_time="2",
            lvl_2_pump_on_time="30",
            lvl_2_pump_off_time="60",
            lvl_3_pump_on_time="60",
            lvl_3_pump_off_time="30",
            low_battery_thold="9.6",
            lost_alarm_interval="10",
            heartbeat_interval="60",
            setup_duration="5"))
        self.notify_commands_changed()

    def create_profile(self) -> sdk.Profile:
        profile: sdk.Profile = self.profile_db.get(self._profile.id) if self._profile else sdk.Profile()
        profile.name = 'New Profile'
        self.profile_db.add(profile)
        self.notify_profiles_changed()
        return profile

    def remove_profile(self) -> None:
        self.profile_db.remove(self.profile)
        self.notify_profiles_changed()

    def save_profile(self):
        self.profile_db.edit(self.profile)
        self.notify_profiles_changed()

    @property
    def profile(self) -> Optional[sdk.Profile]:
        return self._profile

    @profile.setter
    def profile(self, value: Optional[sdk.Profile]) -> None:
        self._profile = value

    def is_profile_temp_lvl_2_thold_valid(self) -> bool:
        if not (isinstance(self.profile.temp_lvl_2_thold, str) and
                sdk.floatable(self.profile.temp_lvl_2_thold) and
                14 <= float(self.profile.temp_lvl_2_thold) <= 99):
            return False
        return True

    def is_profile_temp_lvl_3_thold_valid(self) -> bool:
        if not (isinstance(self.profile.temp_lvl_3_thold, str) and
                sdk.floatable(self.profile.temp_lvl_3_thold) and
                14 <= float(self.profile.temp_lvl_3_thold) <= 99):
            return False
        return True

    def is_profile_temp_lvl_4_thold_valid(self) -> bool:
        if not (isinstance(self.profile.temp_lvl_4_thold, str) and
                sdk.floatable(self.profile.temp_lvl_4_thold) and
                14 <= float(self.profile.temp_lvl_4_thold) <= 99):
            return False
        return True

    def is_profile_temp_sensitivity_valid(self) -> bool:
        if not (isinstance(self.profile.temp_sensitivity, str) and
                sdk.floatable(self.profile.temp_sensitivity) and
                0.1 <= float(self.profile.temp_sensitivity) <= 3):
            return False
        return True

    def is_profile_temp_detection_interval_valid(self) -> bool:
        if not (isinstance(self.profile.temp_detection_interval, str) and
                self.profile.temp_detection_interval.isnumeric() and
                1 <= int(self.profile.temp_detection_interval) <= 600):
            return False
        return True

    def is_profile_scale_of_pump_on_time_valid(self) -> bool:
        if not (isinstance(self.profile.scale_of_pump_on_time, str) and
                sdk.floatable(self.profile.scale_of_pump_on_time) and
                1 <= float(self.profile.scale_of_pump_on_time) <= 10):
            return False
        return True

    def is_profile_lvl_2_pump_on_time_valid(self) -> bool:
        if not (isinstance(self.profile.lvl_2_pump_on_time, str) and
                self.profile.lvl_2_pump_on_time.isnumeric() and
                30 <= int(self.profile.lvl_2_pump_on_time) <= 600):
            return False
        return True

    def is_profile_lvl_2_pump_off_time_valid(self) -> bool:
        if not (isinstance(self.profile.lvl_2_pump_off_time, str) and
                self.profile.lvl_2_pump_off_time.isnumeric() and
                30 <= int(self.profile.lvl_2_pump_off_time) <= 600):
            return False
        return True

    def is_profile_lvl_3_pump_on_time_valid(self) -> bool:
        if not (isinstance(self.profile.lvl_3_pump_on_time, str) and
                self.profile.lvl_3_pump_on_time.isnumeric() and
                30 <= int(self.profile.lvl_3_pump_on_time) <= 600):
            return False
        return True

    def is_profile_lvl_3_pump_off_time_valid(self) -> bool:
        if not (isinstance(self.profile.lvl_3_pump_off_time, str) and
                self.profile.lvl_3_pump_off_time.isnumeric() and
                30 <= int(self.profile.lvl_3_pump_off_time) <= 600):
            return False
        return True

    def is_profile_low_battery_thold_valid(self) -> bool:
        if not (isinstance(self.profile.low_battery_thold, str) and
                sdk.floatable(self.profile.low_battery_thold) and
                3 <= float(self.profile.low_battery_thold) <= 6):
            return False
        return True

    def is_profile_lost_alarm_interval_valid(self) -> bool:
        if not (isinstance(self.profile.lost_alarm_interval, str) and
                self.profile.lost_alarm_interval.isnumeric() and
                1 <= int(self.profile.lost_alarm_interval) <= 300):
            return False
        return True

    def is_profile_heartbeat_interval_valid(self) -> bool:
        if not (isinstance(self.profile.heartbeat_interval, str) and
                self.profile.heartbeat_interval.isnumeric() and
                1 <= int(self.profile.heartbeat_interval) <= 180):
            return False
        return True

    def is_profile_setup_duration_valid(self) -> bool:
        if not (isinstance(self.profile.setup_duration, str) and
                self.profile.setup_duration.isnumeric() and
                1 <= int(self.profile.setup_duration) <= 10):
            return False
        return True

    def is_profile_valid(self) -> bool:
        return all([
            self.is_profile_temp_lvl_2_thold_valid(),
            self.is_profile_temp_lvl_3_thold_valid(),
            self.is_profile_temp_lvl_4_thold_valid(),
            self.is_profile_temp_sensitivity_valid(),
            self.is_profile_temp_detection_interval_valid(),
            self.is_profile_scale_of_pump_on_time_valid(),
            self.is_profile_lvl_2_pump_on_time_valid(),
            self.is_profile_lvl_2_pump_off_time_valid(),
            self.is_profile_lvl_3_pump_on_time_valid(),
            self.is_profile_lvl_3_pump_off_time_valid(),
            self.is_profile_low_battery_thold_valid(),
            self.is_profile_lost_alarm_interval_valid(),
            self.is_profile_heartbeat_interval_valid(),
            self.is_profile_setup_duration_valid(),
        ])

    @property
    def profiles(self) -> list[sdk.Profile]:
        if not list(self.profile_db.get_all()):
            self.generate_default_profiles()
        return list(self.profile_db.get_all())

    def add_on_commands_changed_listener(self, listener: Callable[[list[sdk.Command]], None]) -> None:
        self._commands_changed_listeners.append(listener)

    def notify_commands_changed(self) -> None:
        commands = self.commands
        listener: Callable[[list[sdk.Command]], None]
        for listener in self._commands_changed_listeners:
            listener(commands)

    def generate_default_commands(self) -> None:
        self.command_db.add(sdk.Command(
            name="Trigger immediately (countdown 0 second)",
            command="CD0"))
        self.command_db.add(sdk.Command(
            name="Countdown 2 seconds",
            command="CD2"))
        self.command_db.add(sdk.Command(
            name="SD2",
            command="SD2"))
        self.command_db.add(sdk.Command(
            name="TD4",
            command="TD4"))
        self.notify_commands_changed()

    def create_command(self) -> sdk.Command:
        command: sdk.Command = sdk.Command(name="New Command")
        self.command_db.add(command)
        self.notify_commands_changed()
        return command

    def remove_command(self) -> None:
        self.command_db.remove(self.command)
        self.notify_commands_changed()

    def save_command(self):
        self.command_db.edit(self.command)
        self.notify_commands_changed()

    @property
    def command(self) -> Optional[sdk.Command]:
        return self._command

    @command.setter
    def command(self, value: Optional[sdk.Command]) -> None:
        self._command = value

    @property
    def commands(self) -> list[sdk.Command]:
        if not list(self.command_db.get_all()):
            self.generate_default_commands()
        return list(self.command_db.get_all())

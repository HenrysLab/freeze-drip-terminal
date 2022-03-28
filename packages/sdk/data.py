import dataclasses
import pathlib
from typing import Any, Iterable, Optional

import dacite
import dataset

from .util import Singleton


@dataclasses.dataclass
class Profile:
    id: Optional[int] = None
    name: Optional[str] = None
    temp_lvl_2_thold: Optional[str] = None
    temp_lvl_3_thold: Optional[str] = None
    temp_lvl_4_thold: Optional[str] = None
    temp_sensitivity: Optional[str] = None
    temp_detection_interval: Optional[str] = None
    scale_of_pump_on_time: Optional[str] = None
    lvl_2_pump_on_time: Optional[str] = None
    lvl_2_pump_off_time: Optional[str] = None
    lvl_3_pump_on_time: Optional[str] = None
    lvl_3_pump_off_time: Optional[str] = None
    low_battery_thold: Optional[str] = None
    lost_alarm_interval: Optional[str] = None
    heartbeat_interval: Optional[str] = None
    setup_duration: Optional[str] = None


class ProfileDatabase(Singleton):
    def __init__(self, path: pathlib.Path):
        self.path: pathlib.Path = path
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            tx.get_table('profile') if 'profile' in tx.tables else tx.create_table('profile')

    def add(self, profile: Profile) -> None:
        profile_dict: dict[str, Any] = dataclasses.asdict(profile)
        profile_dict['id'] = None
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            profile_table: dataset.Table = tx.get_table('profile')
            profile_table.insert(profile_dict)
            profile_table.create_index(['id'])

    def edit(self, profile: Profile) -> None:
        if not self.path.exists():
            raise FileNotFoundError("database is absent")
        if not isinstance(profile.id, int):
            raise KeyError("no id provided")
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            if 'profile' not in tx.tables:
                raise ValueError('profile table is not in the database yet')
            profile_table: dataset.Table = tx.get_table('profile')
            profile_table.update(dataclasses.asdict(profile), ['id'])

    def get(self, id_: int) -> Profile:
        if not self.path.exists():
            raise FileNotFoundError("database is absent")
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            if 'profile' not in tx.tables:
                raise ValueError('profile table is not in the database yet')
            profile_table: dataset.Table = tx.get_table('profile')
            res: Optional[dict[str, Any]] = profile_table.find_one(id=id_)
            if not res:
                raise ValueError("no such id")
            return dacite.from_dict(data_class=Profile, data=res)

    def get_all(self) -> Iterable[Profile]:
        if not self.path.exists():
            raise FileNotFoundError("database is absent")
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            if 'profile' not in tx.tables:
                return map(lambda _: _, ())
            profile_table: dataset.Table = tx.get_table('profile')
            return map(lambda x: dacite.from_dict(data_class=Profile, data=x), profile_table.find())

    def remove(self, profile: Profile) -> None:
        if not self.path.exists():
            raise FileNotFoundError("database is absent")
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            if 'profile' not in tx.tables:
                raise ValueError('profile table is not in the database yet')
            profile_table: dataset.Table = tx.get_table('profile')
            if not profile_table.find_one(id=profile.id):
                raise ValueError("no such id")
            profile_table.delete(id=profile.id)


@dataclasses.dataclass
class Command:
    id: Optional[int] = None
    name: Optional[str] = None
    command: Optional[str] = None


class CommandDatabase(Singleton):
    def __init__(self, path: pathlib.Path):
        self.path: pathlib.Path = path
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            tx.get_table('command') if 'command' in tx.tables else tx.create_table('command')

    def add(self, command: Command) -> None:
        command_dict: dict[str, Any] = dataclasses.asdict(command)
        command_dict['id'] = None
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            command_table: dataset.Table = tx.get_table('command')
            command_table.insert(command_dict)
            command_table.create_index(['id'])

    def edit(self, command: Command) -> None:
        if not self.path.exists():
            raise FileNotFoundError("database is absent")
        if not isinstance(command.id, int):
            raise KeyError("no id provided")
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            if 'command' not in tx.tables:
                raise ValueError('command table is not in the database yet')
            command_table: dataset.Table = tx.get_table('command')
            command_table.update(dataclasses.asdict(command), ['id'])

    def get(self, id_: int) -> Command:
        if not self.path.exists():
            raise FileNotFoundError("database is absent")
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            if 'command' not in tx.tables:
                raise ValueError('command table is not in the database yet')
            command_table: dataset.Table = tx.get_table('command')
            res: Optional[dict[str, Any]] = command_table.find_one(id=id_)
            if not res:
                raise ValueError("no such id")
            return dacite.from_dict(data_class=Command, data=res)

    def get_all(self) -> Iterable[Command]:
        if not self.path.exists():
            raise FileNotFoundError("database is absent")
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            if 'command' not in tx.tables:
                return map(lambda _: _, ())
            command_table: dataset.Table = tx.get_table('command')
            return map(lambda x: dacite.from_dict(data_class=Command, data=x), command_table.find())

    def remove(self, command: Command) -> None:
        if not self.path.exists():
            raise FileNotFoundError("database is absent")
        tx: dataset.Database
        with dataset.connect(f'sqlite:///{str(self.path)}') as tx:
            if 'command' not in tx.tables:
                raise ValueError('command table is not in the database yet')
            command_table: dataset.Table = tx.get_table('command')
            if not command_table.find_one(id=command.id):
                raise ValueError("no such id")
            command_table.delete(id=command.id)

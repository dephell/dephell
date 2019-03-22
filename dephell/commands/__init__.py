# app
from .config import ConfigCommand
from .convert import ConvertCommand
from .create import CreateCommand
from .destroy import DestroyCommand
from .get import GetCommand
from .info import InfoCommand
from .init import InitCommand
from .install import InstallCommand
from .shell import ShellCommand


__all__ = [
    'commands',
    'ConfigCommand',
    'ConvertCommand',
    'CreateCommand',
    'DestroyCommand',
    'GetCommand',
    'InfoCommand',
    'InitCommand',
    'InstallCommand',
    'ShellCommand',
]


commands = dict(
    config=ConfigCommand,
    convert=ConvertCommand,
    create=CreateCommand,
    destroy=DestroyCommand,
    get=GetCommand,
    info=InfoCommand,
    init=InitCommand,
    install=InstallCommand,
    shell=ShellCommand,
)

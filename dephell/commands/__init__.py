# app
from .config import ConfigCommand
from .convert import ConvertCommand
from .create import CreateCommand
from .destroy import DestroyCommand
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
    info=InfoCommand,
    init=InitCommand,
    install=InstallCommand,
    shell=ShellCommand,
)

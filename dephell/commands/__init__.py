# app
from .config import ConfigCommand
from .convert import ConvertCommand
from .info import InfoCommand
from .init import InitCommand
from .install import InstallCommand
from .shell import ShellCommand


__all__ = [
    'commands',
    'ConfigCommand',
    'ConvertCommand',
    'InfoCommand',
    'InitCommand',
    'InstallCommand',
    'ShellCommand',
]


commands = dict(
    config=ConfigCommand,
    convert=ConvertCommand,
    info=InfoCommand,
    init=InitCommand,
    install=InstallCommand,
    shell=ShellCommand,
)

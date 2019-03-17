# app
from .config import ConfigCommand
from .convert import ConvertCommand
from .info import InfoCommand
from .init import InitCommand
from .shell import ShellCommand


__all__ = [
    'commands',
    'ConfigCommand',
    'ConvertCommand',
    'InfoCommand',
    'InitCommand',
    'ShellCommand',
]


commands = dict(
    config=ConfigCommand,
    convert=ConvertCommand,
    info=InfoCommand,
    init=InitCommand,
    shell=ShellCommand,
)

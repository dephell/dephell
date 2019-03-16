# app
from .config import ConfigCommand
from .convert import ConvertCommand
from .init import InitCommand
from .shell import ShellCommand


__all__ = [
    'commands',
    'ConfigCommand',
    'ConvertCommand',
    'InitCommand',
    'ShellCommand',
]


commands = dict(
    config=ConfigCommand,
    convert=ConvertCommand,
    init=InitCommand,
    shell=ShellCommand,
)

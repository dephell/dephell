# app
from .config import ConfigCommand
from .convert import ConvertCommand
from .init import InitCommand


__all__ = [
    'commands',
    'ConfigCommand',
    'ConvertCommand',
    'InitCommand',
]


commands = dict(
    config=ConfigCommand,
    convert=ConvertCommand,
    init=InitCommand,
)

# app
from .convert import ConvertCommand
from .init import InitCommand


__all__ = ['ConvertCommand', 'InitCommand', 'commands']


commands = dict(
    convert=ConvertCommand,
    init=InitCommand,
)

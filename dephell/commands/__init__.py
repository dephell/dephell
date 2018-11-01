from .convert import ConvertCommand


__all__ = ['ConvertCommand', 'commands']


commands = dict(
    convert=ConvertCommand,
)

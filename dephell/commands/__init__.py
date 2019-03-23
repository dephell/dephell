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


commands = {
    'init': InitCommand,

    'deps convert': ConvertCommand,
    'deps install': InstallCommand,
    # 'deps sync': ...,
    # 'deps remove': ...,

    'jail install': GetCommand,
    # 'jail update': ...,
    # 'jail remove': ...,

    'venv create': CreateCommand,
    'venv shell': ShellCommand,
    'venv destroy': DestroyCommand,

    'inspect config': ConfigCommand,
    'inspect venv': InfoCommand,
}

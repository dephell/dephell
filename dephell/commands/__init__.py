# app
from .config import InspectConfigCommand
from .convert import DepsConvertCommand
from .create import VenvCreateCommand
from .destroy import VenvDestroyCommand
from .get import JailInstallCommand
from .info import InspectVenvCommand
from .init import InitCommand
from .install import DepsInstallCommand
from .shell import VenvShellCommand


__all__ = [
    'commands',
    'InspectConfigCommand',
    'DepsConvertCommand',
    'VenvCreateCommand',
    'VenvDestroyCommand',
    'JailInstallCommand',
    'InspectVenvCommand',
    'InitCommand',
    'DepsInstallCommand',
    'VenvShellCommand',
]


commands = {
    'init': InitCommand,

    'deps convert': DepsConvertCommand,
    'deps install': DepsInstallCommand,
    # 'deps sync': ...,
    # 'deps remove': ...,

    'jail install': JailInstallCommand,
    # 'jail update': ...,
    # 'jail remove': ...,

    'venv create': VenvCreateCommand,
    'venv shell': VenvShellCommand,
    'venv destroy': VenvDestroyCommand,

    'inspect config': InspectConfigCommand,
    'inspect venv': InspectVenvCommand,
}

# app
from .deps_convert import DepsConvertCommand
from .deps_install import DepsInstallCommand
from .init import InitCommand
from .inspect_config import InspectConfigCommand
from .inspect_venv import InspectVenvCommand
from .jail_install import JailInstallCommand
from .venv_create import VenvCreateCommand
from .venv_destroy import VenvDestroyCommand
from .venv_shell import VenvShellCommand


__all__ = [
    'commands',
    'DepsConvertCommand',
    'DepsInstallCommand',
    'InitCommand',
    'InspectConfigCommand',
    'InspectVenvCommand',
    'JailInstallCommand',
    'VenvCreateCommand',
    'VenvDestroyCommand',
    'VenvShellCommand',
]


commands = {
    'deps convert': DepsConvertCommand,
    'deps install': DepsInstallCommand,
    # 'deps remove': ...,
    # 'deps sync': ...,
    'init': InitCommand,
    'inspect config': InspectConfigCommand,
    'inspect venv': InspectVenvCommand,
    'jail install': JailInstallCommand,
    # 'jail update': ...,
    # 'jail remove': ...,
    'venv create': VenvCreateCommand,
    'venv destroy': VenvDestroyCommand,
    'venv shell': VenvShellCommand,
}

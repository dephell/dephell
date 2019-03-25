# app
from .build import BuildCommand
from .deps_convert import DepsConvertCommand
from .deps_install import DepsInstallCommand
from .init import InitCommand
from .inspect_config import InspectConfigCommand
from .inspect_venv import InspectVenvCommand
from .install import InstallCommand
from .jail_install import JailInstallCommand
from .jail_remove import JailRemoveCommand
from .run import RunCommand
from .venv_create import VenvCreateCommand
from .venv_destroy import VenvDestroyCommand
from .venv_shell import VenvShellCommand


__all__ = [
    'commands',
    'BuildCommand',
    'DepsConvertCommand',
    'DepsInstallCommand',
    'InitCommand',
    'InspectConfigCommand',
    'InspectVenvCommand',
    'InstallCommand',
    'JailInstallCommand',
    'JailRemoveCommand',
    'RunCommand',
    'VenvCreateCommand',
    'VenvDestroyCommand',
    'VenvShellCommand',
]


commands = {
    'build': BuildCommand,
    'deps convert': DepsConvertCommand,
    'deps install': DepsInstallCommand,
    # 'deps remove': ...,
    # 'deps sync': ...,
    'init': InitCommand,
    'inspect config': InspectConfigCommand,
    'inspect venv': InspectVenvCommand,
    'install': InstallCommand,
    'jail install': JailInstallCommand,
    'jail remove': JailRemoveCommand,
    # 'jail update': ...,
    'run': RunCommand,
    'venv create': VenvCreateCommand,
    'venv destroy': VenvDestroyCommand,
    'venv shell': VenvShellCommand,
}

# app
from .build import BuildCommand
from .deps_convert import DepsConvertCommand
from .deps_install import DepsInstallCommand
from .deps_licenses import DepsLicensesCommand
from .generate_authors import GenerateAuthorsCommand
from .generate_config import GenerateConfigCommand
from .generate_editorconfig import GenerateEditorconfigCommand
from .generate_license import GenerateLicenseCommand
from .inspect_config import InspectConfigCommand
from .inspect_venv import InspectVenvCommand
from .install import InstallCommand
from .jail_install import JailInstallCommand
from .jail_remove import JailRemoveCommand
from .venv_create import VenvCreateCommand
from .venv_destroy import VenvDestroyCommand
from .venv_run import VenvRunCommand
from .venv_shell import VenvShellCommand


__all__ = [
    'BuildCommand',
    'commands',
    'DepsConvertCommand',
    'DepsInstallCommand',
    'DepsLicensesCommand',
    'GenerateAuthorsCommand',
    'GenerateConfigCommand',
    'GenerateEditorconfigCommand',
    'GenerateLicenseCommand',
    'InspectConfigCommand',
    'InspectVenvCommand',
    'InstallCommand',
    'JailInstallCommand',
    'JailRemoveCommand',
    'VenvCreateCommand',
    'VenvDestroyCommand',
    'VenvRunCommand',
    'VenvShellCommand',
]


commands = {
    'build': BuildCommand,
    'deps convert': DepsConvertCommand,
    'deps install': DepsInstallCommand,
    'deps licenses': DepsLicensesCommand,
    # 'deps remove': ...,
    # 'deps sync': ...,
    'generate authors': GenerateAuthorsCommand,
    'generate config': GenerateConfigCommand,
    'generate editorconfig': GenerateEditorconfigCommand,
    'generate license': GenerateLicenseCommand,
    'inspect config': InspectConfigCommand,
    'inspect venv': InspectVenvCommand,
    'install': InstallCommand,
    'jail install': JailInstallCommand,
    'jail remove': JailRemoveCommand,
    # 'jail update': ...,
    'venv create': VenvCreateCommand,
    'venv destroy': VenvDestroyCommand,
    'venv run': VenvRunCommand,
    'venv shell': VenvShellCommand,
}

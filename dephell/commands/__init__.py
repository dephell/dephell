# app
from .autocomplete import AutocompleteCommand
from .deps_add import DepsAddCommand
from .deps_audit import DepsAuditCommand
from .deps_convert import DepsConvertCommand
from .deps_install import DepsInstallCommand
from .deps_licenses import DepsLicensesCommand
from .deps_outdated import DepsOutdatedCommand
from .deps_tree import DepsTreeCommand
from .generate_authors import GenerateAuthorsCommand
from .generate_config import GenerateConfigCommand
from .generate_editorconfig import GenerateEditorconfigCommand
from .generate_license import GenerateLicenseCommand
from .inspect_config import InspectConfigCommand
from .inspect_gadget import InspectGadgetCommand
from .inspect_self import InspectSelfCommand
from .inspect_venv import InspectVenvCommand
from .jail_install import JailInstallCommand
from .jail_list import JailListCommand
from .jail_remove import JailRemoveCommand
from .package_downloads import PackageDownloadsCommand
from .package_install import PackageInstallCommand
from .package_list import PackageListCommand
from .package_search import PackageSearchCommand
from .package_show import PackageShowCommand
from .project_build import ProjectBuildCommand
from .project_bump import ProjectBumpCommand
from .project_test import ProjectTestCommand
from .venv_create import VenvCreateCommand
from .venv_destroy import VenvDestroyCommand
from .venv_run import VenvRunCommand
from .venv_shell import VenvShellCommand


__all__ = [
    'AutocompleteCommand',
    'commands',
    'DepsAddCommand',
    'DepsAuditCommand',
    'DepsConvertCommand',
    'DepsInstallCommand',
    'DepsLicensesCommand',
    'DepsOutdatedCommand',
    'DepsTreeCommand',
    'GenerateAuthorsCommand',
    'GenerateConfigCommand',
    'GenerateEditorconfigCommand',
    'GenerateLicenseCommand',
    'InspectConfigCommand',
    'InspectGadgetCommand',
    'InspectSelfCommand',
    'InspectVenvCommand',
    'JailInstallCommand',
    'JailListCommand',
    'JailRemoveCommand',
    'PackageDownloadsCommand',
    'PackageInstallCommand',
    'PackageListCommand',
    'PackageSearchCommand',
    'PackageShowCommand',
    'ProjectBuildCommand',
    'ProjectBumpCommand',
    'ProjectTestCommand',
    'VenvCreateCommand',
    'VenvDestroyCommand',
    'VenvRunCommand',
    'VenvShellCommand',
]


commands = {
    'autocomplete': AutocompleteCommand,
    'deps add': DepsAddCommand,
    'deps audit': DepsAuditCommand,
    'deps convert': DepsConvertCommand,
    'deps install': DepsInstallCommand,
    'deps licenses': DepsLicensesCommand,
    'deps outdated': DepsOutdatedCommand,
    'deps tree': DepsTreeCommand,
    # 'deps remove': ...,
    # 'deps sync': ...,
    'generate authors': GenerateAuthorsCommand,
    'generate config': GenerateConfigCommand,
    'generate editorconfig': GenerateEditorconfigCommand,
    'generate license': GenerateLicenseCommand,
    'inspect config': InspectConfigCommand,
    'inspect self': InspectSelfCommand,
    'inspect venv': InspectVenvCommand,
    'inspect gadget': InspectGadgetCommand,
    'jail install': JailInstallCommand,
    'jail list': JailListCommand,
    'jail remove': JailRemoveCommand,
    # 'jail update': ...,
    'package downloads': PackageDownloadsCommand,
    'package install': PackageInstallCommand,
    'package list': PackageListCommand,
    'package search': PackageSearchCommand,
    'package show': PackageShowCommand,
    'project build': ProjectBuildCommand,
    'project bump': ProjectBumpCommand,
    'project test': ProjectTestCommand,
    'venv create': VenvCreateCommand,
    'venv destroy': VenvDestroyCommand,
    'venv run': VenvRunCommand,
    'venv shell': VenvShellCommand,
}

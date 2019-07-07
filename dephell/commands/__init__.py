# app
from .auth import AuthCommand
from .autocomplete import AutocompleteCommand
from .deps_add import DepsAddCommand
from .deps_audit import DepsAuditCommand
from .deps_check import DepsCheckCommand
from .deps_convert import DepsConvertCommand
from .deps_install import DepsInstallCommand
from .deps_licenses import DepsLicensesCommand
from .deps_outdated import DepsOutdatedCommand
from .deps_sync import DepsSyncCommand
from .deps_tree import DepsTreeCommand
from .generate_authors import GenerateAuthorsCommand
from .generate_config import GenerateConfigCommand
from .generate_editorconfig import GenerateEditorconfigCommand
from .generate_license import GenerateLicenseCommand
from .generate_travis import GenerateTravisCommand
from .inspect_auth import InspectAuthCommand
from .inspect_config import InspectConfigCommand
from .inspect_gadget import InspectGadgetCommand
from .inspect_self import InspectSelfCommand
from .inspect_venv import InspectVenvCommand
from .jail_install import JailInstallCommand
from .jail_list import JailListCommand
from .jail_remove import JailRemoveCommand
from .jail_try import JailTryCommand
from .package_downloads import PackageDownloadsCommand
from .package_install import PackageInstallCommand
from .package_list import PackageListCommand
from .package_purge import PackagePurgeCommand
from .package_releases import PackageReleasesCommand
from .package_remove import PackageRemoveCommand
from .package_search import PackageSearchCommand
from .package_show import PackageShowCommand
from .project_build import ProjectBuildCommand
from .project_bump import ProjectBumpCommand
from .project_test import ProjectTestCommand
from .vendor_download import VendorDownloadCommand
from .vendor_import import VendorImportCommand
from .venv_create import VenvCreateCommand
from .venv_destroy import VenvDestroyCommand
from .venv_run import VenvRunCommand
from .venv_shell import VenvShellCommand


COMMANDS = {
    'auth': AuthCommand,
    'autocomplete': AutocompleteCommand,

    'deps add': DepsAddCommand,
    'deps audit': DepsAuditCommand,
    'deps check': DepsCheckCommand,
    'deps convert': DepsConvertCommand,
    'deps install': DepsInstallCommand,
    'deps licenses': DepsLicensesCommand,
    'deps outdated': DepsOutdatedCommand,
    'deps sync': DepsSyncCommand,
    'deps tree': DepsTreeCommand,
    # 'deps remove': ...,

    'generate authors': GenerateAuthorsCommand,
    'generate config': GenerateConfigCommand,
    'generate editorconfig': GenerateEditorconfigCommand,
    'generate license': GenerateLicenseCommand,
    'generate travis': GenerateTravisCommand,

    'inspect auth': InspectAuthCommand,
    'inspect config': InspectConfigCommand,
    'inspect self': InspectSelfCommand,
    'inspect venv': InspectVenvCommand,
    'inspect gadget': InspectGadgetCommand,

    'jail install': JailInstallCommand,
    'jail list': JailListCommand,
    'jail remove': JailRemoveCommand,
    'jail try': JailTryCommand,
    # 'jail update': ...,

    'package downloads': PackageDownloadsCommand,
    'package install': PackageInstallCommand,
    'package list': PackageListCommand,
    'package purge': PackagePurgeCommand,
    'package releases': PackageReleasesCommand,
    'package remove': PackageRemoveCommand,
    'package search': PackageSearchCommand,
    'package show': PackageShowCommand,

    'project build': ProjectBuildCommand,
    'project bump': ProjectBumpCommand,
    'project test': ProjectTestCommand,

    'vendor download': VendorDownloadCommand,
    'vendor import': VendorImportCommand,

    'venv create': VenvCreateCommand,
    'venv destroy': VenvDestroyCommand,
    'venv run': VenvRunCommand,
    'venv shell': VenvShellCommand,
}

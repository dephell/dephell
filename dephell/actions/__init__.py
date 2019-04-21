"""Actions are functions that used only in commands
"""

# app
from ._autocomplete import make_bash_autocomplete, make_zsh_autocomplete
from ._converting import attach_deps
from ._dotenv import read_dotenv
from ._downloads import get_downloads_by_category, get_total_downloads
from ._editorconfig import make_editorconfig
from ._entrypoints import get_entrypoints
from ._git import git_commit, git_tag
from ._json import make_json
from ._package import get_package, get_packages, get_resolver
from ._python import get_python, get_python_env
from ._roman import arabic2roman, roman2arabic
from ._shutil import format_size, get_path_size
from ._travis import make_travis
from ._venv import get_venv
from ._version import bump_file, bump_project, bump_version, get_version_from_file, get_version_from_project


__all__ = [
    'arabic2roman',
    'attach_deps',
    'bump_file',
    'bump_project',
    'bump_version',
    'format_size',
    'get_downloads_by_category',
    'get_entrypoints',
    'get_package',
    'get_packages',
    'get_path_size',
    'get_python_env',
    'get_python',
    'get_resolver',
    'get_total_downloads',
    'get_venv',
    'get_version_from_file',
    'get_version_from_project',
    'git_commit',
    'git_tag',
    'make_bash_autocomplete',
    'make_editorconfig',
    'make_json',
    'make_travis',
    'make_zsh_autocomplete',
    'read_dotenv',
    'roman2arabic',
]

# built-in
import os
import platform
from collections import OrderedDict
from enum import Enum, unique
from types import MappingProxyType


@unique
class ReturnCodes(Enum):
    OK = 0
    COMMAND_ERROR = 1
    INVALID_CONFIG = 2
    UNKNOWN_EXCEPTION = 3


IS_WINDOWS = (os.name == 'nt') or (platform.system() == 'Windows')

CONFIG_NAMES = ('poetry.toml', 'pyproject.toml')
GLOBAL_CONFIG_NAME = 'config.toml'

DEFAULT_WAREHOUSE = 'https://pypi.org/pypi/'
WAREHOUSE_DOMAINS = {'pypi.org', 'pypi.python.org', 'test.pypi.org'}

FORMATS = (
    'conda',
    'egginfo',
    'flit',
    'imports',
    'installed',
    'pip',
    'pipfile',
    'pipfilelock',
    'piplock',
    'poetry',
    'poetrylock',
    'pyproject',
    'sdist',
    'setuppy',
    'wheel',
)
NON_PATH_FORMATS = ('imports', 'installed')

FILES = (
    'setup.py',
    'pyproject.toml', 'pyproject.lock',
    'requirements.in', 'requirements.txt',
    'Pipfile', 'Pipfile.lock',
    'environment.yml', 'environment.yaml',
)

SUFFIXES = ('.txt', '.in', '.lock', '.toml', '.egg-info', '.py', '.json')

PAIRS = (
    ('pip',     'piplock'),
    ('pipfile', 'pipfilelock'),
    ('poetry',  'poetrylock'),
    ('poetry',  'setuppy'),
    ('setuppy', 'sdist'),
    ('setuppy', 'wheel'),
)

STRATEGIES = ('min', 'max')
REPOSITORIES = ('pypi', 'conda', 'conda_git', 'conda_cloud')

LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'EXCEPTION')
LOG_FORMATTERS = ('short', 'full')

# https://github.com/github/markup
EXTENSIONS = MappingProxyType(OrderedDict([
    ('rst',         'rst'),

    ('md',          'md'),
    ('markdown',    'md'),
    ('mdown',       'md'),
    ('mkd',         'md'),
    ('mkdn',        'md'),

    ('txt',         'txt'),
    ('',            'txt'),
]))


ARCHIVE_EXTENSIONS = (
    '.tar.bz2',
    '.tar.gz',
    '.tar.lz',
    '.tar.lzma',
    '.tar.xz',
    '.tar',
    '.tbz',
    '.tgz',
    '.tlz',
    '.txz',
    '.whl',
    '.zip',
)


DEPHELL_ECOSYSTEM = (
    'dephell_archive',
    'dephell_discover',
    'dephell_licenses',
    'dephell_links',
    'dephell_markers',
    'dephell_pythons',
    'dephell_shells',
    'dephell_specifier',
    'dephell_venvs',
    'dephell_versioning',
)

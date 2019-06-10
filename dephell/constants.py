# built-in
import os
import platform
from collections import OrderedDict
from datetime import date
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

# about name aliases: https://github.com/semver/semver/issues/411
VERSION_MAJOR = ('major', 'breaking')
VERSION_MINOR = ('minor', 'feature')
VERSION_PATCH = ('patch', 'fix', 'micro')
VERSION_PRE = ('pre', 'rc', 'alpha')
VERSION_PRE_MAJOR = ('premajor', 'prebreaking')
VERSION_PRE_MINOR = ('preminor', 'prefeature')
VERSION_PRE_PATCH = ('prepatch', 'prefix', 'premicro')
PRE_VERSIONS = VERSION_PRE + VERSION_PRE_MAJOR + VERSION_PRE_MINOR + VERSION_PRE_PATCH
MAJOR_VERSIONS = VERSION_MAJOR + VERSION_PRE_MAJOR
MINOR_VERSIONS = VERSION_MINOR + VERSION_PRE_MINOR
PATCH_VERSIONS = VERSION_PATCH + VERSION_PRE_PATCH
VERSION_RELEASE = ('release', )
# semver has no post-releases: https://github.com/semver/semver/issues/200
VERSION_POST = ('post', )
VERSION_DEV = ('dev', )
VERSION_LOCAL = ('local', )
VERSION_SCHEMES = MappingProxyType(dict(
    # https://www.python.org/dev/peps/pep-0440/#version-scheme
    pep=sum([
        MAJOR_VERSIONS,
        MINOR_VERSIONS,
        PATCH_VERSIONS,
        VERSION_PRE,
        VERSION_POST,
        VERSION_DEV,
        VERSION_LOCAL,
        VERSION_RELEASE,
    ], ()),
    # https://semver.org/
    semver=MAJOR_VERSIONS + MINOR_VERSIONS + PATCH_VERSIONS + VERSION_PRE + VERSION_LOCAL + VERSION_RELEASE,
    # https://github.com/staltz/comver
    comver=MAJOR_VERSIONS + MINOR_VERSIONS + VERSION_PRE + VERSION_LOCAL + VERSION_RELEASE,
    # http://dafoster.net/articles/2015/03/14/semantic-versioning-vs-romantic-versioning/
    romver=MAJOR_VERSIONS + MINOR_VERSIONS + VERSION_PRE + VERSION_RELEASE,
    # https://calver.org/
    calver=VERSION_MAJOR + VERSION_PATCH,
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#serial-versioning
    serial=VERSION_MAJOR,
    # Mac OS X reference
    roman=VERSION_MAJOR,
    # https://0ver.org/
    zerover=MINOR_VERSIONS + PATCH_VERSIONS + VERSION_PRE + VERSION_LOCAL + VERSION_RELEASE,
))
VERSION_INIT = MappingProxyType(dict(
    pep='0.1.0',
    semver='0.1.0',
    comver='0.1',
    romver='0.1.0',
    calver='{}.{}'.format(date.today().year, date.today().month),
    roman='I',
))


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
)

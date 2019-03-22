
# built-in
from collections import OrderedDict
from enum import Enum, unique
from types import MappingProxyType


@unique
class ReturnCodes(Enum):
    OK = 0
    COMMAND_ERROR = 1
    INVALID_CONFIG = 2
    UNKNOWN_EXCEPTION = 3


@unique
class JoinTypes(Enum):
    AND = 1
    OR = 2


FORMATS = (
    'egginfo',
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

FILES = (
    'requirements.in', 'requirements.txt',
    'Pipfile', 'Pipfile.lock',
    'pyproject.toml', 'pyproject.lock',
    'setup.py',
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

ENVS = ('main', 'dev', 'main-opt', 'dev-opt')

STRATEGIES = ('min', 'max')

LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'EXCEPTION')
LOG_FORMATTERS = ('short', 'full')

PYTHONS_DEPRECATED = ('2.6', '2.7', '3.0', '3.1', '3.2', '3.3', '3.4')
PYTHONS_POPULAR = ('3.5', '3.6', '3.7')
PYTHONS_UNRELEASED = ('3.8', '4.0')
PYTHONS = PYTHONS_POPULAR + PYTHONS_DEPRECATED + PYTHONS_UNRELEASED

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

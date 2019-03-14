# built-in
from enum import Enum, unique


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
    'setuppy',
    'wheel',
)

FILES = (
    'requirements.in', 'requirements.txt',
    'Pipfile', 'Pipfile.lock',
    'pyproject.toml', 'pyproject.lock',
    'setup.py',
)

ENVS = ('main', 'dev', 'main-opt', 'dev-opt')

STRATEGIES = ('min', 'max')

LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR')

PYTHONS = (
    '2.7',                          # deprecated
    '3.0', '3.1', '3.2', '3.3',     # very seldom
    '3.4', '3.5', '3.6', '3.7',     # most popular
    '3.8', '3.9', '4.0', '4.1',     # unreleased
)

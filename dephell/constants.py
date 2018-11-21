# built-in
from enum import Enum, unique


CACHE_DIR = '.dephell'


@unique
class ReturnCodes(Enum):
    OK = 0
    COMMAND_ERROR = 1
    INVALID_CONFIG = 2
    UNKNOWN_EXCEPTION = 3


FORMATS = (
    'pip',      'piplock',
    'pipfile',  'pipfilelock',
    'poetry',   'poetrylock',
    'setuppy',
)

FILES = (
    'requirements.in',  'requirements.txt',
    'Pipfile',          'Pipfile.lock',
    'pyproject.toml',   'pyproject.lock',
    'setup.py',
)

ENVS = ('main', 'dev', 'main-opt', 'dev-opt')

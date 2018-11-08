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
)

FILES = (
    'requirements.in',  'requirements.txt',
    'Pipfile',          'Pipfile.lock',
    'pyproject.toml',   'pyproject.lock',
)

ENVS = ('main', 'dev', 'main-opt', 'dev-opt')

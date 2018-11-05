from enum import Enum, unique


@unique
class ReturnCodes(Enum):
    OK = 1
    COMMAND_ERROR = 2
    INVALID_CONFIG = 3
    UNKNOWN_EXCEPTION = 4

# built-in
import logging
import os


__all__ = ['ColoredFormatter', 'LevelFilter']


try:
    try:
        from colorama import Fore, init
    except ImportError:
        from pip._vendor.colorama import Fore, init
    init()
except ImportError:
    Fore = None


class _ForeAnsi:
    _f = '\x1b[{}m'.format

    BLACK = _f(30)
    RED = _f(31)
    GREEN = _f(32)
    YELLOW = _f(33)
    BLUE = _f(34)
    MAGENTA = _f(35)
    CYAN = _f(36)
    WHITE = _f(37)
    RESET = _f(39)


class _ForeWin:
    _f = '\x1b[{}m'.format

    BLACK = _f(30)
    RED = _f(31)
    GREEN = _f(32)
    YELLOW = _f(33)
    BLUE = _f(34)
    MAGENTA = _f(35)
    CYAN = _f(36)
    WHITE = _f(37)
    RESET = _f(39)


if Fore is None:
    if os.name == 'nt':
        Fore = _ForeAnsi
    else:
        Fore = _ForeWin


COLORS = {
    'DEBUG': Fore.BLUE,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRITICAL': Fore.CYAN,
}

# http://docs.python.org/library/logging.html#logrecord-attributes
RESERVED_ATTRS = (
    'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
    'funcName', 'levelname', 'levelno', 'lineno', 'module',
    'msecs', 'message', 'msg', 'name', 'pathname', 'process',
    'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName',
)


# https://github.com/madzak/python-json-logger/blob/master/src/pythonjsonlogger/jsonlogger.py
def merge_record_extra(record, target, reserved):
    """
    Merges extra attributes from LogRecord object into target dictionary
    :param record: logging.LogRecord
    :param target: dict to update
    :param reserved: dict or list with reserved keys to skip
    """
    for key, value in record.__dict__.items():
        # this allows to have numeric keys
        if key not in reserved:
            if not hasattr(key, 'startswith') or not key.startswith('_'):
                target[key] = value
    return target


# https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, colors=True, extras=True, traceback=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors
        self.extras = extras
        self.traceback = traceback

    def format(self, record):
        # add color
        if self.colors and record.levelname in COLORS:
            start = COLORS[record.levelname]
            record.levelname = start + record.levelname + Fore.RESET
            record.msg = Fore.WHITE + record.msg + Fore.RESET

        # add extras
        if self.extras:
            extras = merge_record_extra(record=record, target=dict(), reserved=RESERVED_ATTRS)
            record.extras = ', '.join('{}={}'.format(k, v) for k, v in extras.items())
            if record.extras:
                record.extras = Fore.MAGENTA + '({})'.format(record.extras) + Fore.RESET

        # hide traceback
        if not self.traceback:
            record.exc_text = None
            record.exc_info = None
            record.stack_info = None

        return super().format(record)


class LevelFilter(logging.Filter):
    """Filter log by min or max severity level.
    """
    def __init__(self, low=logging.DEBUG, high=logging.CRITICAL):
        # Convert str level representation to level number.
        # Example: "DEBUG" -> 10
        if isinstance(low, str):
            low = getattr(logging, low)
        if isinstance(high, str):
            high = getattr(logging, high)

        self._low = low
        self._high = high
        super().__init__()

    def filter(self, record):
        if self._low <= record.levelno <= self._high:
            return True
        return False

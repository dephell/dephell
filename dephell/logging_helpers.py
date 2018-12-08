# built-in
import logging


__all__ = ['ColoredFormatter', 'LevelFilter']


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;{:d}m"
BOLD_SEQ = "\033[1m"

COLORS = {
    'DEBUG': BLUE,
    'INFO': GREEN,
    'WARNING': YELLOW,
    'ERROR': RED,
    'CRITICAL': CYAN,
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
    def __init__(self, *args, colors=True, extras=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors
        self.extras = extras

    def format(self, record):
        # add color
        if self.colors and record.levelname in COLORS:
            start = COLOR_SEQ.format(COLORS[record.levelname])
            record.levelname = start + record.levelname + RESET_SEQ
            record.msg = COLOR_SEQ.format(WHITE) + record.msg + RESET_SEQ

        # add extras
        if self.extras:
            extras = merge_record_extra(record=record, target=dict(), reserved=RESERVED_ATTRS)
            record.extras = ', '.join('{}={}'.format(k, v) for k, v in extras.items())
            if record.extras:
                record.extras = COLOR_SEQ.format(MAGENTA) + '({})'.format(record.extras) + RESET_SEQ

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

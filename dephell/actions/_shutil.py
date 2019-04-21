# built-in
from os.path import getsize
from pathlib import Path


def get_path_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return getsize(str(path))
    total = 0
    for subpath in path.glob('**/*'):
        if subpath.is_file():
            total += getsize(str(subpath))
    return total


def format_size(size: int) -> str:
    for delimeter, suffix in ((2 ** 20, 'Mb'), (1024, 'Kb')):
        formatted = size / delimeter
        if formatted >= 1:
            return '{:.2f}{}'.format(formatted, suffix)
    return str(size) + 'b'

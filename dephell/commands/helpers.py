from collections import defaultdict

# external
from dephell_pythons import Python, Pythons

# app
from ..converters import CONVERTERS
from ..config import Config


def _each(value):
    new_value = defaultdict(list)
    for line in value:
        for name, field in line.items():
            new_value[name].append(field)
    return new_value


FILTERS = {
    'first()': lambda v: v[0],
    'last()': lambda v: v[-1],
    'len()': lambda v: len(v),
    'max()': lambda v: max(v),
    'min()': lambda v: min(v),
    'reverse()': lambda v: v[::-1],
    'type()': lambda v: type(v).__name__,
    'each()': _each,

    # aliases
    'latest()': lambda v: v[-1],
    'length()': lambda v: len(v),
    'reversed()': lambda v: v[::-1],
}


def getitem(value, key):
    filter = FILTERS.get(key)
    if filter is not None:
        return filter(value)
    if key.isdigit():
        key = int(key)
    return value[key]


def get_python(config: Config) -> Python:
    pythons = Pythons()

    # defined in config
    python = config.get('python')
    if python:
        return pythons.get_best(python)

    # defined in dependency file
    loader = CONVERTERS[config['from']['format']]
    root = loader.load(path=config['from']['path'])
    if root.python:
        return pythons.get_by_spec(root.python)

    return pythons.current

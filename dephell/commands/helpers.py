from collections import defaultdict

# external
from dephell_pythons import Python, Pythons

# app
from ..converters import CONVERTERS
from ..config import Config


def _each(value):
    if isinstance(value, list):
        new_value = defaultdict(list)
        for line in value:
            for name, field in line.items():
                new_value[name].append(field)
        return dict(new_value)

    new_value = []
    for line in zip(*value.values()):
        new_value.append(dict(zip(value.keys(), line)))
    return new_value


FILTERS = {
    'each()': _each,
    'first()': lambda v: v[0],
    'last()': lambda v: v[-1],
    'len()': lambda v: len(v),
    'max()': lambda v: max(v),
    'min()': lambda v: min(v),
    'reverse()': lambda v: v[::-1],
    'sort()': lambda v: sorted(v),
    'type()': lambda v: type(v).__name__,
    'zip()': lambda v: list(map(list, zip(*v))),

    # aliases
    '#': _each,
    'latest()': lambda v: v[-1],
    'length()': lambda v: len(v),
    'reversed()': lambda v: v[::-1],
    'size()': lambda v: len(v),
    'sorted()': lambda v: sorted(v),
}


def getitem(value, key):
    # function
    filter = FILTERS.get(key)
    if filter is not None:
        return filter(value)

    # sum of fields
    if '+' in key:
        keys = key.split('+')
        return {key: value[key] for key in keys}

    # index
    if key.isdigit():
        key = int(key)
        return value[key]

    # slice
    if ':' in key:
        left, _sep, right = key.partition(':')
        if (not left or left.isdigit()) and (not right or right.isdigit()):
            left = int(left) if left else 0
            right = int(right) if right else None
            return value[left:right]

    # field
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

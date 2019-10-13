# built-in
import json
from collections import defaultdict
from functools import reduce, wraps
from typing import Optional

# external
from pygments import formatters, highlight, lexers
import flatdict
from tabulate import tabulate

# app
from ..config import config


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


def _flatten(value) -> list:
    if not isinstance(value, (list, tuple)):
        return [value]
    new_value = []
    for element in value:
        new_value.extend(_flatten(element))
    return new_value


FILTERS = {
    'each()': _each,
    'first()': lambda v: v[0],
    'flatten()': _flatten,
    'last()': lambda v: v[-1],
    'len()': len,
    'max()': max,
    'min()': min,
    'reverse()': lambda v: v[::-1],
    'sort()': sorted,
    'sum()': sum,
    'type()': lambda v: type(v).__name__,
    'zip()': lambda v: list(map(list, zip(*v))),

    # aliases
    '#': _each,
    'count()': len,
    'flat()': _flatten,
    'latest()': lambda v: v[-1],
    'length()': len,
    'reversed()': lambda v: v[::-1],
    'size()': len,
    'sorted()': sorted,
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


def _jsonify(data, colors: bool = False) -> str:
    json_params = dict(indent=2, sort_keys=True, ensure_ascii=False)
    dumped = json.dumps(data, **json_params)
    if not colors:
        return dumped
    return highlight(dumped, lexers.JsonLexer(), formatters.TerminalFormatter())


def _make_table(json_table: str) -> str:

    # Load the created json as dict
    to_table = json.loads(json_table)

    # Transform it into a flat dictionary
    to_table = flatdict.FlatDict(to_table)

    # Create an array where the first row are the keys
    # the other rows are the value
    to_table = [to_table.keys(), to_table.values()]

    return tabulate(to_table, headers='firstrow', tablefmt='fancy_grid')


def _tabelize(func):

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if not config['table']:
            return func(*args, **kwargs)
        else:
            return _make_table(func(*args, **kwargs))

    return func_wrapper


@_tabelize
def make_json(data, key: str = None, sep: Optional[str] = '-', colors: bool = True) -> str:
    # print all config
    if not key:
        return _jsonify(data=data, colors=colors)

    if sep is None:
        return _jsonify(data=data[key], colors=colors)

    keys = key.replace('.', sep).split(sep)
    value = reduce(getitem, keys, data)
    # print config section
    if isinstance(value, (dict, list)):
        return _jsonify(data=value, colors=colors)

    # print one value
    return str(value)

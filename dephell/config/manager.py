from collections import defaultdict
from typing import Optional

import tomlkit
from cerberus import Validator

from .scheme import SCHEME


class Config:
    def __init__(self, data: Optional[dict] = None):
        self._data = data or dict()

    def attach(self, data: dict, container: Optional[dict] = None):
        if container is None:
            container = self._data
        for key, value in data.items():
            if key not in container:
                container[key] = value
            elif isinstance(value, dict):
                self.attach(data=value, container=container[key])
            else:
                container[key] = value

    def attach_config(self, path: str, env: str) -> dict:
        # read
        with open(path, 'r', encoding='utf8') as stream:
            doc = tomlkit.parse(stream.read())

        # get section
        if 'tool' not in doc or 'dephell' not in doc['tool']:
            raise KeyError('section [tool.dephell...] not found')
        data = dict(doc['tool']['dephell'])

        # get env
        if env not in data:
            raise KeyError('env not found')
        data = data[env]

        self.attach(data)
        return data

    def attach_cli(self, args, sep: str = '_'):
        data = defaultdict(dict)
        for name, value in args._get_kwargs():
            parsed = name.split(sep, maxsplit=1)
            if len(parsed) == 1:
                data[name] = value
            else:
                data[parsed[0]][parsed[1]] = value
        self.attach(data)
        return data

    def validate(self) -> bool:
        validator = Validator(SCHEME)
        result = validator.validate(self._data)
        self.errors = validator.errors
        return result

    def format_errors(self) -> str:
        result = []
        for field, errors in self.errors:
            result.append(field)
            for error in errors:
                result.append('    ' + error)
        return '\n'.join(result)

    def __getattr__(self, name):
        return getattr(self._data, name)

    def __getitem__(self, name):
        return self._data[name]

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            repr(self._data),
        )

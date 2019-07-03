# built-in
import json
from collections import defaultdict
from logging import captureWarnings
from logging.config import dictConfig
from pathlib import Path
from typing import Dict, Optional

# external
import tomlkit
from cerberus import Validator

# app
from ..constants import SUFFIXES, NON_PATH_FORMATS
from .defaults import DEFAULT
from .logging_config import LOGGING
from .scheme import SCHEME


class Config:
    env = ''
    _skip = (
        'config', 'env',
        'key', 'name', 'type',
        'hostname', 'username', 'password',
    )

    def __init__(self, data: Optional[dict] = None):
        self._data = data or DEFAULT.copy()

    def setup_logging(self, data: Optional[dict] = None) -> None:
        captureWarnings(True)
        if data is None:
            data = LOGGING
            if self._data:
                data['loggers']['dephell']['level'] = self['level']
                for formatter in data['formatters'].values():
                    formatter['colors'] = not self['nocolors']
                    formatter['traceback'] = self['traceback']
                for handler in data['handlers'].values():
                    handler['formatter'] = self['format']
        dictConfig(LOGGING)

    def attach(self, data: dict, container: Optional[dict] = None) -> None:
        if container is None:
            container = self._data

        for section in ('from', 'to'):
            if section in data and isinstance(data[section], str):
                data[section] = self._expand_converter(data[section])

        for key, value in data.items():
            if value is None:
                continue

            # convert `and` section from tomlkit types to python types
            if isinstance(value, (list, tuple)):
                new_value = []
                for subvalue in value:
                    if isinstance(subvalue, dict):
                        subvalue = dict(subvalue)
                    new_value.append(subvalue)
                value = new_value

            if key not in container:
                container[key] = value
            elif isinstance(value, dict):
                self.attach(data=value, container=container[key])
            else:
                container[key] = value

    @staticmethod
    def _expand_converter(text: str) -> Dict[str, str]:
        from ..converters import CONVERTERS

        # passed converter that doesn't require path
        if text in NON_PATH_FORMATS:
            return dict(format=text, path='')

        # if passed only format
        if text in CONVERTERS:
            converter = CONVERTERS[text]
            for path in Path('.').iterdir():
                if path.suffix in SUFFIXES:
                    content = None if not path.is_file() else path.read_text()
                    if converter.can_parse(path=path, content=content):
                        return dict(format=text, path=str(path))
            raise LookupError('cannot find file for converter: ' + str(text))

        # if passed only filename
        path = Path(text)
        content = None if not path.is_file() else path.read_text()
        for name, converter in CONVERTERS.items():
            if converter.can_parse(path=path, content=content):
                return dict(format=name, path=text)

        raise LookupError('cannot determine converter for file: ' + str(text))

    def attach_file(self, path: str, env: str, silent: bool = False) -> Optional[dict]:
        # read
        with open(path, 'r', encoding='utf8') as stream:
            doc = tomlkit.parse(stream.read())

        # get section
        if 'tool' not in doc or 'dephell' not in doc['tool']:
            if silent:
                return None
            raise KeyError('section [tool.dephell...] not found')
        data = dict(doc['tool']['dephell'])

        # get env
        if env not in data:
            raise KeyError('env `{}` not found'.format(env))
        data = data[env]

        self.attach(data)
        self.env = env
        return data

    def attach_cli(self, args, sep: str = '_') -> dict:
        data = defaultdict(dict)
        for name, value in args._get_kwargs():
            if value is None or value is False:
                continue
            parsed = name.split(sep, maxsplit=1)
            if len(parsed) == 1:
                data[name] = value
            else:
                # if old content isn't a dict, override it
                if not isinstance(data[parsed[0]], dict):
                    data[parsed[0]] = dict()
                data[parsed[0]][parsed[1]] = value
        self.attach(data)
        return dict(data)

    def validate(self) -> bool:
        self._data = {k: v for k, v in self._data.items() if k not in self._skip}
        validator = Validator(SCHEME)
        result = validator.validate(self._data)
        self.errors = validator.errors
        return result

    def format_errors(self) -> str:
        return json.dumps(self.errors, indent=2, sort_keys=True)

    def __getattr__(self, name):
        return getattr(self._data, name)

    def __getitem__(self, name: str):
        return self._data[name]

    def __contains__(self, name: str):
        return name in self._data

    def __repr__(self):
        return '{cls}({data})'.format(
            cls=type(self).__name__,
            data=repr(self._data),
        )

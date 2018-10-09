import tomlkit


DEFAULTS = dict(
    pip='requirements.in',
    piplock='requirements.txt',
    pipfile='Pipfile',
    pipfilelock='Pipfile.lock',
    poetry='pyproject.toml',
    poetrylock='pyproject.lock',
)


class Config:
    def __init__(self, data: dict):
        self._data = data

    @classmethod
    def load(cls, path: str):
        with open(path, 'r', encoding='utf8') as stream:
            doc = tomlkit.parse(stream.read())
        if 'tool' not in doc or 'dephell' not in doc['tool']:
            raise KeyError('section [tool.dephell...] not found')
        data = dict(doc['tool']['dephell'])
        return cls(data)

    def get(self, env: str) -> dict:
        if env not in self._data:
            raise KeyError('environment not found', env)

        config = self._data[env]
        for key in ('from', 'to'):
            if key not in config:
                raise KeyError('key "{}" not found'.format(key))
            config[key] = self._process_line(key=key, line=config[key])
        return config

    @staticmethod
    def _process_line(key: str, line) -> dict:
        if isinstance(line, str):
            line = dict(format=line)
        if 'format' not in line:
            raise KeyError('format required for "{}"'.format(key))
        if line['format'] not in DEFAULTS:
            raise KeyError('invalid format "{}". Available: {}'.format(
                line['format'],
                ', '.join(DEFAULTS),
            ))
        if 'path' not in line:
            line['path'] = DEFAULTS[line['format']]
        return line

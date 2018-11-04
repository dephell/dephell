from collections import namedtuple
from pathlib import Path

import tomlkit

from ..config import Config
from .base import BaseCommand


Rule = namedtuple('Rule', ['from_path', 'to_path', 'from_format', 'to_format'])

rules = (
    Rule(
        from_path='requirements.in',
        to_path='requirements.txt',
        from_format='pip',
        to_format='piplock',
    ),
    Rule(
        from_path='requirements.txt',
        to_path='requirements.lock',
        from_format='pip',
        to_format='piplock',
    ),
    Rule(
        from_path='Pipfile',
        to_path='Pipfile.lock',
        from_format='pipfile',
        to_format='pipfilelock',
    ),
    Rule(
        from_path='pyproject.toml',
        to_path='pyproject.lock',
        from_format='poetry',
        to_format='poetry.toml',
    ),
)

example_rule = Rule(
    from_path='requirements.in',
    to_path='requirements.txt',
    from_format='pip',
    to_format='piplock',
)


class InitCommand(BaseCommand):
    @classmethod
    def get_config(cls, args):
        config = Config()
        return config

    def validate(self):
        pass

    @staticmethod
    def _make_env(rule):
        table = tomlkit.table()

        table['from'] = tomlkit.inline_table()
        table['from']['format'] = rule.from_format
        table['from']['path'] = rule.from_path

        table['to'] = tomlkit.inline_table()
        table['to']['format'] = rule.to_format
        table['to']['path'] = rule.to_path

        table['silent'] = False

        return table

    def __call__(self):
        config_path = Path(self.args.config)
        if config_path.exists():
            # read
            with config_path.open('r', encoding='utf8') as stream:
                doc = tomlkit.parse(stream.read())
        else:
            doc = tomlkit.document()

        # add section
        if 'tool' not in doc:
            doc.add('tool', tomlkit.table())
        if 'dephell' not in doc['tool']:
            doc['tool'].add('dephell', tomlkit.table())

        # detect requirements files
        path = Path(self.args.config).parent
        for rule in rules:
            if (path / rule.from_path).exists():
                doc['tool']['dephell'].add(rule.from_format, self._make_env(rule))

        if not doc['tool']['dephell'].value:
            doc['tool']['dephell'].add('example', self._make_env(example_rule))

        # write
        with config_path.open('w', encoding='utf8') as stream:
            stream.write(tomlkit.dumps(doc))

        return True

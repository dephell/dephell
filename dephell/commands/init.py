from collections import defaultdict
from pathlib import Path

import tomlkit

from ..config import Config


Rule = defaultdict('Rule', ['from_path', 'to_path', 'from_format', 'to_format'])

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


class InitCommand:
    @classmethod
    def get_config(cls, args):
        config = Config()
        return config

    def validate(self):
        pass

    def __call__(self):
        # read
        with open(self.args.config, 'r', encoding='utf8') as stream:
            doc = tomlkit.parse(stream.read())

        # add section
        if 'tool' not in doc:
            doc.add('tool', tomlkit.table())
        if 'dephell' not in doc['tool']:
            doc['tool'].add('dephell', tomlkit.table())

        # detect requirements files
        path = Path(self.args.config).parent
        for rule in rules:
            if (path / rule.from_path).exists():
                table = tomlkit.table()

                table['from'] = tomlkit.inline_table()
                table['from']['format'] = rule.from_format
                table['from']['path'] = rule.from_path

                table['to'] = tomlkit.inline_table()
                table['to']['format'] = rule.to_format
                table['to']['path'] = rule.to_path

                table['silent'] = False

                doc.add(rule.from_format, table)

        # write
        with open(self.args.config, 'w', encoding='utf8') as stream:
            stream.write(tomlkit.dumps(doc))

        return True

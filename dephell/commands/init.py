# built-in
from pathlib import Path
from argparse import ArgumentParser

# external
import huepy
import tomlkit

# app
from ..config import Config
from ..config import builders
from ..rules import EXAMPLE_RULE, RULES
from .base import BaseCommand


class InitCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell init',
            description='Create config file for dephell',
        )
        builders.build_config(parser)
        return parser

    @classmethod
    def get_config(cls, args):
        config = Config()
        return config

    def validate(self):
        return True

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
        exists = config_path.exists()
        if exists:
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
        for rule in RULES:
            if (path / rule.from_path).exists():
                if rule.from_format not in doc['tool']['dephell']:
                    doc['tool']['dephell'].add(
                        rule.from_format,
                        self._make_env(rule),
                    )

        if not doc['tool']['dephell'].value:
            if 'example' not in doc['tool']['dephell']:
                doc['tool']['dephell'].add(
                    'example',
                    self._make_env(EXAMPLE_RULE),
                )

        # write
        with config_path.open('w', encoding='utf8') as stream:
            stream.write(tomlkit.dumps(doc))

        if exists:
            print(huepy.good('pyproject.toml updated'))
        else:
            print(huepy.good('pyproject.toml created'))
        return True

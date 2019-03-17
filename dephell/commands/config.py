from argparse import ArgumentParser

# app
from .base import BaseCommand
from ..config import builders


class ConfigCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell config',
            description='Show current config',
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_to(parser)
        builders.build_resolver(parser)
        builders.build_api(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('key', nargs='?')
        return parser

    def __call__(self):
        print(self.get_value(data=self.config._data, key=self.args.key))

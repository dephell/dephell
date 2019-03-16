import json
from argparse import ArgumentParser
from functools import reduce
from operator import getitem

# app
from .base import BaseCommand
from ..config import builders


class ConfigCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell config',
            description='Convert dependencies between formats',
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
        # print all config
        if not self.args.key:
            print(json.dumps(self.config._data, indent=2, sort_keys=True))
            return True

        keys = self.args.key.split('-')
        value = reduce(getitem, keys, self.config)
        # print config section
        if type(value) is dict:
            print(json.dumps(value, indent=2, sort_keys=True))
            return True

        # print one value
        print(value)
        return True

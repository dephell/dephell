# built-in
from argparse import ArgumentParser

# app
from ..actions import make_json
from ..config import builders
from .base import BaseCommand


class InspectConfigCommand(BaseCommand):
    """Show current config.

    https://dephell.readthedocs.io/en/latest/cmd-inspect-config.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell inspect config',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_to(parser)
        builders.build_resolver(parser)
        builders.build_api(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        print(make_json(data=self.config._data, key=self.config.get('filter')))
        return True

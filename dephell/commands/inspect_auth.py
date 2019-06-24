# built-in
from argparse import ArgumentParser

# app
from ..actions import make_json
from ..config import builders
from .base import BaseCommand


class InspectAuthCommand(BaseCommand):
    """Show saved credentials.

    https://dephell.readthedocs.io/cmd-inspect-auth.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell inspect config',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        return parser

    def __call__(self) -> bool:
        print(make_json(data=self.config['auth'], key=self.config.get('filter')))
        return True

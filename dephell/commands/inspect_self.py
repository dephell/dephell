# built-in
import sys
from argparse import ArgumentParser
from pathlib import Path

# app
from ..__version__ import __version__
from ..actions import make_json
from ..config import builders
from .base import BaseCommand


class InspectSelfCommand(BaseCommand):
    """Show information about DepHell installation.

    https://dephell.readthedocs.io/en/latest/cmd-inspect-self.html
    """
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell inspect self',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self):
        data = dict(
            path=str(Path(__file__).parent.parent),
            python=sys.executable,
            version=__version__,
        )
        print(make_json(data=data, key=self.config.get('filter')))
        return True

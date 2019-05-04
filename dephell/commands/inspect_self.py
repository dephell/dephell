# built-in
import sys
from argparse import ArgumentParser
from pathlib import Path

# app
from .. import __version__
from ..actions import format_size, get_path_size, make_json
from ..config import builders
from ..constants import DEPHELL_ECOSYSTEM
from ..converters import InstalledConverter
from .base import BaseCommand


class InspectSelfCommand(BaseCommand):
    """Show information about DepHell installation.

    https://dephell.readthedocs.io/en/latest/cmd-inspect-self.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell inspect self',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        installed = InstalledConverter().load(names=DEPHELL_ECOSYSTEM)
        versions = dict()
        for dep in installed.dependencies:
            versions[dep.name] = str(dep.constraint).replace('=', '')

        data = dict(
            path=str(Path(__file__).parent.parent),
            python=sys.executable,
            version=__version__,
            versions=versions,
            cache=format_size(get_path_size(Path(self.config['cache']['path']))),
        )
        print(make_json(data=data, key=self.config.get('filter')))
        return True

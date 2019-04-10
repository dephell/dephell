# built-in
from argparse import REMAINDER, ArgumentParser

# app
from ..actions import make_json
from ..config import builders
from ..repositories import WareHouseRepo
from .base import BaseCommand


class PackageSearchCommand(BaseCommand):
    """Search packages on PyPI.org

    https://dephell.readthedocs.io/en/latest/cmd-package-search.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell package search',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='package name or other search keywords')
        return parser

    def __call__(self) -> bool:
        repo = WareHouseRepo()
        results = repo.search(self.args.name)
        print(make_json(data=results, key=self.config.get('filter')))
        return True

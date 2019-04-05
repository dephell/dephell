# built-in
from argparse import ArgumentParser

# app
from ..actions import make_json, get_total_downloads, get_downloads_by_category
from ..config import builders
from .base import BaseCommand


class PackageDownloadsCommand(BaseCommand):
    """Show downloads statistic for package from PyPI.org.

    https://dephell.readthedocs.io/en/latest/cmd-package-downloads.html
    """

    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell package downloads',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', help='package name')
        return parser

    def __call__(self):
        name = self.args.name.lower().replace('_', '-')
        data = dict(
            total=get_total_downloads(name=name),
            pythons=get_downloads_by_category(category='pythons', name=name),
            systems=get_downloads_by_category(category='systems', name=name),
        )

        print(make_json(data=data, key=self.config.get('filter')))
        return True

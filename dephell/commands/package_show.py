# built-in
from argparse import ArgumentParser

# app
from ..controllers import DependencyMaker
from ..config import builders
from ..models import RootDependency
from ..repositories import WareHouseRepo
from .base import BaseCommand


class PackageShowCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell package show',
            description='Show information about package from PyPI.org.',
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', help='package name (and version)')
        parser.add_argument('key', nargs='?', help='key to filter result')
        return parser

    def __call__(self):
        dep = DependencyMaker.from_requirement(source=RootDependency(), req=self.args.name)[0]
        repo = WareHouseRepo()
        releases = repo.get_releases(dep)

        data = dict(
            name=dep.name,
            version=str(releases[0].version),
            description=dep.description,

            license=getattr(dep.license, 'id', dep.license),
            links=dep.links,
            authors=[str(author) for author in dep.authors],
        )
        print(self.get_value(data=data, key=self.args.key))

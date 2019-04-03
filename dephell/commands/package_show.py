# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..controllers import DependencyMaker
from ..config import builders
from ..converters import InstalledConverter
from ..models import RootDependency
from ..repositories import WareHouseRepo
from ..venvs import VEnvs
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
        return parser

    def __call__(self):
        dep = DependencyMaker.from_requirement(source=RootDependency(), req=self.args.name)[0]
        repo = WareHouseRepo()
        releases = repo.get_releases(dep)

        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        path = None
        if venv.exists():
            path = venv.lib_path
        else:
            self.logger.warning('venv not found, package version will be shown for global python lib')

        converter = InstalledConverter()
        root = converter.load(path)
        local_versions = []
        for subdep in root.dependencies:
            if subdep.name == dep.name:
                local_versions = str(subdep.constraint).replace('=', '').split(' || ')

        data = dict(
            name=dep.name,
            version=dict(
                latest=str(releases[0].version),
                installed=local_versions,
            ),
            description=dep.description,

            license=getattr(dep.license, 'id', dep.license),
            links=dep.links,
            updated=str(releases[0].time.date()),
            authors=[str(author) for author in dep.authors],
        )
        print(self.get_value(data=data, key=self.config.get('filter')))
        return True

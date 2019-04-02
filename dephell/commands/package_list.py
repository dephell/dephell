# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..converters import InstalledConverter
from ..repositories import WareHouseRepo
from ..venvs import VEnvs
from .base import BaseCommand


class PackageListCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell package list',
            description='Show all installed packages',
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        return parser

    def __call__(self):
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        path = None
        if venv.exists():
            path = venv.lib_path
        else:
            self.logger.warning('venv not found, package version will be shown for global python lib')

        converter = InstalledConverter()
        root = converter.load(path)

        repo = WareHouseRepo()
        data = []
        for dep in root.dependencies:
            releases = repo.get_releases(dep)
            data.append(dict(
                name=dep.name,
                version=dict(
                    latest=str(releases[0].version),
                    installed=str(dep.constraint).lstrip('='),
                ),
                description=dep.description,

                license=getattr(dep.license, 'id', dep.license),
                links=dep.links,
                authors=[str(author) for author in dep.authors],
            ))
        print(self.get_value(data=data, key=self.config.get('filter')))

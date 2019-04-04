# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..repositories import WareHouseRepo
from .base import BaseCommand
from ..venvs import VEnvs
from ..converters import CONVERTERS, InstalledConverter


class DepsOutdatedCommand(BaseCommand):
    """Show outdated project dependencies.

    https://dephell.readthedocs.io/en/latest/cmd-deps-outdated.html
    """
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell deps outdated',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_to(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        return parser

    def __call__(self):
        root = None

        loader_config = self.config.get('to') or self.config.get('from')
        if loader_config is not None:
            loader = CONVERTERS[loader_config['format']]
            if loader.lock:
                self.logger.info('get dependencies from lockfile', extra=dict(
                    format=loader_config['format'],
                    path=loader_config['path'],
                ))
                root = loader.load(path=loader_config['path'])

        if root is None:
            venvs = VEnvs(path=self.config['venv'])
            venv = venvs.get(Path(self.config['project']), env=self.config.env)
            if venv.exists():
                self.logger.info('get packages from project environment', extra=dict(
                    path=str(venv.path),
                ))
                path = venv.lib_path
            else:
                path = None
                self.logger.info('get packages from global python lib')

            converter = InstalledConverter()
            root = converter.load(path)

        repo = WareHouseRepo()
        data = []
        for dep in root.dependencies:
            releases = repo.get_releases(dep)
            latest = str(releases[0].version)
            installed = str(dep.constraint).replace('=', '').split(' || ')
            if latest in installed:
                continue
            data.append(dict(
                name=dep.name,
                latest=latest,
                installed=installed,
                updated=str(releases[0].time.date()),
                description=dep.description,
            ))
        print(self.get_value(data=data, key=self.config.get('filter')))
        return True

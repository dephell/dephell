# built-in
from argparse import ArgumentParser

# app
from ..actions import get_python_env, make_json
from ..config import builders
from ..converters import CONVERTERS, InstalledConverter
from ..repositories import WareHouseRepo
from .base import BaseCommand


class DepsOutdatedCommand(BaseCommand):
    """Show outdated project dependencies.

    https://dephell.readthedocs.io/en/latest/cmd-deps-outdated.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
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

    def __call__(self) -> bool:
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
            # get executable
            python = get_python_env(config=self.config)
            self.logger.debug('choosen python', extra=dict(path=str(python.path)))
            root = InstalledConverter().load(paths=python.lib_paths)

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

        if data:
            print(make_json(data=data, key=self.config.get('filter')))
            return False

        self.logger.info('all dependencies is up-to-date')
        return True

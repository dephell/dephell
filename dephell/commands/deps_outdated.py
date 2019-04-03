# built-in
from argparse import ArgumentParser

# app
from ..config import builders
from ..repositories import WareHouseRepo
from .base import BaseCommand
from ..converters import CONVERTERS


class DepsOutdatedCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell deps outdated',
            description='Show outdated project dependencies',
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        return parser

    def __call__(self):
        loader_config = self.config.get('to', self.config['from'])
        self.logger.info('get dependencies', extra=dict(
            format=loader_config['format'],
            path=loader_config['path'],
        ))
        loader = CONVERTERS[loader_config['format']]
        root = loader.load(path=loader_config['path'])

        repo = WareHouseRepo()
        data = []
        for dep in root.dependencies:
            releases = repo.get_releases(dep)
            latest = str(releases[0].version)
            installed = str(dep.constraint).lstrip('=')
            if latest == installed:
                continue
            data.append(dict(
                name=dep.name,
                latest=latest,
                locked=installed,
                updated=str(releases[0].time.date()),
                description=dep.description,
            ))
        print(self.get_value(data=data, key=self.config.get('filter')))

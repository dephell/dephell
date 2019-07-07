# built-in
from argparse import ArgumentParser

# app
from ..actions import make_json
from ..config import builders
from .base import BaseCommand


class DepsOutdatedCommand(BaseCommand):
    """Show outdated project dependencies.

    https://dephell.readthedocs.io/cmd-deps-outdated.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell deps outdated',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        resolver = self._get_locked()
        if resolver is None:
            return False

        data = []
        for dep in resolver.graph:
            releases = dep.repo.get_releases(dep)
            latest = str(releases[0].version)
            locked = str(dep.group.best_release.version)
            if latest == locked:
                continue
            data.append(dict(
                name=dep.name,
                latest=latest,
                locked=locked,
                updated=str(releases[0].time.date()),
                description=dep.description,
            ))

        if data:
            print(make_json(data=data, key=self.config.get('filter')))
            return False

        self.logger.info('all dependencies is up-to-date')
        return True

# built-in
from argparse import ArgumentParser

# app
from ..actions import get_package, make_json
from ..config import builders
from .base import BaseCommand


class PackageReleasesCommand(BaseCommand):
    """Show package releases.

    https://dephell.readthedocs.io/cmd-package-releases.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell package releases',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', help='package name')
        return parser

    def __call__(self) -> bool:
        dep = get_package(self.args.name, repo=self.config.get('repo'))
        releases = dep.repo.get_releases(dep)

        data = []
        for release in releases:
            data.append(dict(
                date=str(release.time.date()) if release.time.year != 1970 else None,
                version=str(release.version),
                python=str(release.python) if release.python else '*',
            ))

        if not data:
            self.logger.error('no releases')
            return False
        print(make_json(data=data, key=self.config.get('filter')))
        return True

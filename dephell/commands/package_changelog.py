# built-in
import os
from argparse import REMAINDER, ArgumentParser

# external
import requests
from dephell_changelogs import get_changelog_url, parse_changelog

# app
from ..config import builders
from .base import BaseCommand


DEFAULT_WIDTH = int(os.environ.get('COLUMNS', 90))


class PackageChangelogCommand(BaseCommand):
    """Find project changelog.
    """
    # because we don't actually use anything from the config
    find_config = False

    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='package name')
        return parser

    def __call__(self) -> bool:
        url = get_changelog_url(self.args.name[0])
        if not url:
            self.logger.error('cannot find changelog URL')
            return False
        self.logger.debug('changelog url found', extra=dict(url=url))

        response = requests.get(url=url)
        if not response.ok:
            self.logger.error('cannot get changelog content', extra=dict(
                url=url,
                reason=response.reason,
            ))
            return False
        content = response.text

        if len(self.args.name) == 1:
            print(content)
            return True

        changelog = parse_changelog(content=content)
        if len(changelog) == 1:
            self.logger.warning('cannot parse changelog', extra=dict(url=url))
            print(content)
            return True
        self.logger.debug('changelog parsed', extra=dict(versions=list(changelog)))

        for version in self.args.name[1:]:
            if version not in changelog:
                self.logger.error('cannot find version in changelog', extra=dict(
                    url=url,
                    version=version,
                ))
                return False

        for version in self.args.name[1:]:
            print('\n## Release {}\n'.format(version))
            print(changelog[version].strip('\n'))
        return True

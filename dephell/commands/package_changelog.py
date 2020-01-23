# built-in
import os
from argparse import ArgumentParser, REMAINDER
from typing import Dict, Optional

import requests

# app
from ..actions import get_changelog_url, get_package, parse_changelog
from ..config import builders
from .base import BaseCommand


DEFAULT_WIDTH = int(os.environ.get('COLUMNS', 90))


class PackageChangelogCommand(BaseCommand):
    """Find project changelog.
    """
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
        dep = get_package(self.args.name[0], repo=self.config.get('repo'))
        dep.repo.get_releases(dep)  # fetch metainfo
        url = self._get_url(links=dep.links)
        if not url:
            self.logger.error('cannot find changelog URL')
            return False

        response = requests.get(url=url)
        if not response.ok:
            self.logger.error('cannot get changelog content', extra=dict(url=url))
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

    def _get_url(self, links: Dict[str, str]) -> Optional[str]:
        for url in links.values():
            if not url.startswith('http'):
                url = 'https://' + url
            self.logger.debug('found project URL', extra=dict(url=url))
            url = get_changelog_url(base_url=url)
            if url is not None:
                return url

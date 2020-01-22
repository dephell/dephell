# built-in
import webbrowser
from argparse import ArgumentParser, REMAINDER
from typing import Dict, Optional

import requests

# app
from ..actions import get_changelog_url, get_package, parse_changelog
from ..config import builders
from .base import BaseCommand


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

        if len(self.args.name) == 1:
            self._show_url(url=url)
            return True

        # get changelog content
        response = requests.get(url=url)
        if not response.ok:
            self._show_url(url=url)
            return True

        # extract changelog for the given version
        version = self.args.name[1]
        changelog = parse_changelog(response.text)
        if version not in changelog:
            self._show_url(url=url)
            return True

        print(changelog[version])
        return True

    def _get_url(self, links: Dict[str, str]) -> Optional[str]:
        for url in links.values():
            if not url.startswith('http'):
                url = 'https://' + url
            self.logger.debug('found project URL', extra=dict(url=url))
            url = get_changelog_url(base_url=url)
            if url is not None:
                return url

    def _show_url(self, url):
        self.logger.info('found changelog URL', extra=dict(url=url))
        webbrowser.open_new_tab(url=url)

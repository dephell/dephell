# built-in
import webbrowser
from argparse import ArgumentParser
from typing import Dict, Optional

# app
from ..actions import get_changelog_url, get_package
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
        parser.add_argument('name', help='package name')
        return parser

    def __call__(self) -> bool:
        dep = get_package(self.args.name, repo=self.config.get('repo'))
        dep.repo.get_releases(dep)  # fetch metainfo
        url = self._get_url(links=dep.links)
        if not url:
            self.logger.error('cannot find changelog URL')
            return False
        webbrowser.open_new_tab(url=url)
        return True

    @staticmethod
    def _get_url(links: Dict[str, str]) -> Optional[str]:
        for url in links.values():
            if not url.startswith('http'):
                url = 'https://' + url
            url = get_changelog_url(base_url=url)
            if url is not None:
                return url

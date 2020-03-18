# built-in
import webbrowser
from argparse import ArgumentParser
from typing import Dict, Optional
from urllib.parse import urlparse

# external
import requests

# app
from ..actions import get_package
from ..config import builders
from .base import BaseCommand


class PackageBugCommand(BaseCommand):
    """Report bug in a package.
    """
    find_config = False

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
            self.logger.error('cannot find bug tracker URL')
            return False
        webbrowser.open_new_tab(url=url)
        return True

    @staticmethod
    def _get_url(links: Dict[str, str]) -> Optional[str]:
        # try to find githab or gitlub url and use it as a bug tracker
        for url in links.values():
            if not url.startswith('http'):
                url = 'https://' + url
            parsed = urlparse(url)
            if parsed.hostname not in ('github.com', 'gitlab.com', 'bitbucket.org'):
                continue

            # build URL
            parts = parsed.path.strip('/').split('/')
            if len(parts) < 2:
                continue
            url = 'https://{}/{}/{}/issues/new'.format(parsed.hostname, *parts)

            # check that issues aren't disabled for the project
            response = requests.head(url)
            if response.status_code == 404:
                continue

            return url

        # try to find custom bug tracker by name
        for name, url in links.items():
            if 'tracker' not in name.lower():
                continue
            if not url.startswith('http'):
                url = 'https://' + url
            return url

        return None

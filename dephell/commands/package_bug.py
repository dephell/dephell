# built-in
import webbrowser
from argparse import ArgumentParser
from typing import Optional
from urllib.parse import urlparse

# app
from ..actions import get_package
from ..config import builders
from .base import BaseCommand


class PackageBugCommand(BaseCommand):
    """Report bug in a package.
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
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
        url = self._get_url(dep=dep)
        if not url:
            self.logger.error('cannot find Github URL')
            return False
        webbrowser.open_new_tab(url=url)
        return True

    @staticmethod
    def _get_url(dep) -> Optional[str]:
        for url in dep.links.values():
            if not url.startswith('http'):
                url = 'https://' + url
            parsed = urlparse(url)
            if parsed.hostname != 'github.com':
                continue
            parts = parsed.path.strip('/').split('/')
            if len(parts) < 2:
                continue
            return 'https://github.com/{}/{}/issues/new'.format(*parts)
        return None

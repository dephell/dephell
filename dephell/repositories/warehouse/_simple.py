# built-in
from logging import getLogger
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

# external
import attr
import requests
from packaging.requirements import Requirement

# app
from ..cache import JSONCache
from ..config import config
from ..exceptions import PackageNotFoundError
from ..models.release import Release
from .base import Interface


logger = getLogger('dephell.repositories.warehouse.simple')


def _process_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname == 'pypi.python.org':
        hostname = 'pypi.org'
    else:
        hostname = parsed.hostname
    return parsed.scheme + '://' + hostname + parsed.path


@attr.s()
class SimpleWareHouseRepo(Interface):
    name = attr.ib(default='pypi')
    url = attr.ib(type=str, factory=lambda: config['warehouse'], converter=_process_url)
    prereleases = attr.ib(type=bool, factory=lambda: config['prereleases'])  # allow prereleases
    propagate = True  # deps of deps will inherit repo

    @property
    def pretty_url(self) -> str:
        return self.url

    def get_releases(self, dep) -> tuple:
        # retrieve data
        cache = JSONCache('simple', 'releases', dep.base_name, ttl=config['cache']['ttl'])
        data = cache.load()
        if data is None:
            url = self.url + dep.base_name
            response = requests.get(url)
            if response.status_code == 404:
                raise PackageNotFoundError(package=dep.base_name, url=url)
            response.raise_for_status()
            ...
            cache.dump(data)

        # init releases
        releases = []
        for version, info in data['releases'].items():
            # ignore version if no files for release
            if not info:
                continue
            release = Release.from_response(...)
            # filter prereleases if needed
            if release.version.is_prerelease and not self.prereleases and not dep.prereleases:
                continue
            releases.append(release)
        releases.sort(reverse=True)
        return tuple(releases)

    async def get_dependencies(self, name: str, version: str,
                               extra: Optional[str] = None) -> Tuple[Requirement, ...]:
        ...

    def search(self, query: Iterable[str]) -> List[Dict[str, str]]:
        results = []
        ...
        return results

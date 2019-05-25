from functools import lru_cache
from urllib.parse import urljoin, urlparse
from typing import Optional, Iterable, List, Dict

import attr
import requests
from requests.exceptions import SSLError

from ...config import config
from ...exceptions import PackageNotFoundError
from ..base import Interface
from ._api import WarehouseAPIRepo
from ._simple import WarehouseSimpleRepo


@lru_cache(maxsize=16)
def _has_api(url: str) -> bool:
    if urlparse(url).hostname in ('pypi.org', 'python.org', 'test.pypi.org'):
        return True
    full_url = urljoin(url, 'dephell/json/')
    try:
        response = requests.head(full_url)
    except SSLError:
        return False
    return response.status_code < 400


@attr.s()
class WarehouseRepo(Interface):
    repos = attr.ib(factory=list)
    prereleases = attr.ib(type=bool, factory=lambda: config['prereleases'])  # allow prereleases
    propagate = True  # deps of deps will inherit repo

    def add_repo(self, *, url, name=None):
        if not urlparse(url).scheme:
            url = 'https://' + url
        if name is None:
            name = urlparse(url).hostname
        if _has_api(url=url):
            cls = WarehouseAPIRepo
        else:
            cls = WarehouseSimpleRepo
        self.repos.append(cls(name=name, url=url, prereleases=self.prereleases))

    def get_releases(self, dep) -> tuple:
        first_exception = None
        for repo in self.repos:
            try:
                return repo.get_releases(dep=dep)
            except PackageNotFoundError as exc:
                if first_exception is None:
                    first_exception = exc
        raise first_exception

    async def get_dependencies(self, name: str, version: str, extra: Optional[str] = None) -> tuple:
        first_exception = None
        for repo in self.repos:
            try:
                return await repo.get_dependencies(name=name, version=version, extra=extra)
            except PackageNotFoundError as exc:
                if first_exception is None:
                    first_exception = exc
        raise first_exception

    def search(self, query: Iterable[str]) -> List[Dict[str, str]]:
        for repo in self.repos:
            if isinstance(repo, WarehouseAPIRepo):
                return repo.search(query=query)
        ...
        raise NotImplementedError

    # properties

    @property
    def name(self) -> str:
        return self.repos[0].name

    @property
    def url(self) -> str:
        return self.repos[0].url

    @property
    def pretty_url(self):
        return self.url

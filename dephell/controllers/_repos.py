from functools import lru_cache
from urllib.parse import urljoin, urlparse
from typing import Optional, Iterable, List, Dict

import attr
import requests
from requests.exceptions import SSLError, ConnectionError

from ..config import config
from ..exceptions import PackageNotFoundError
from ..repositories.base import Interface
from ..repositories import WarehouseAPIRepo, WarehouseSimpleRepo


@lru_cache(maxsize=16)
def _has_api(url: str) -> bool:
    if urlparse(url).hostname in ('pypi.org', 'python.org', 'test.pypi.org'):
        return True
    full_url = urljoin(url, 'dephell/json/')
    try:
        response = requests.head(full_url)
    except (SSLError, ConnectionError):
        return False
    return response.status_code < 400


@attr.s()
class RepositoriesRegistry(Interface):
    repos = attr.ib(factory=list)
    prereleases = attr.ib(type=bool, factory=lambda: config['prereleases'])  # allow prereleases

    _urls = attr.ib(factory=set)

    def add_repo(self, *, url: str, name: str = None) -> None:
        if not urlparse(url).scheme:
            url = 'https://' + url
        if url in self._urls:
            return
        if name is None:
            name = urlparse(url).hostname
        if _has_api(url=url):
            cls = WarehouseAPIRepo
        else:
            cls = WarehouseSimpleRepo
        self._urls.add(url)
        self.repos.append(cls(name=name, url=url, prereleases=self.prereleases))

    def make(self, name: str) -> 'RepositoriesRegistry':
        """Return new RepositoriesRegistry where repo with given name goes first
        """
        repos = []
        for repo in self.repos:
            if repo.name == name:
                repos.append(repo)
                break
        else:
            raise LookupError('cannot find repo with given name: {}'.format(name))
        for repo in self.repos:
            if repo.name != name:
                repos.append(repo)
        return type(self)(repos=repos)

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
        return self.repos[0].search(query=query)

    # properties

    @property
    def name(self) -> str:
        return self.repos[0].name

    @property
    def url(self) -> str:
        return self.repos[0].url

    @property
    def pretty_url(self) -> str:
        return self.url

    @property
    def propagate(self) -> bool:
        return self.repos[0].propagate

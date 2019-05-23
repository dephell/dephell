# built-in
import re
from logging import getLogger
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse, urljoin, parse_qs

# external
import attr
import html
import html5lib
import requests
from packaging.requirements import Requirement

# app
from ..cache import JSONCache
from ..config import config
from ..exceptions import PackageNotFoundError
from ..models.release import Release
from .base import Interface


logger = getLogger('dephell.repositories.warehouse.simple')
REX_WORD = re.compile('[a-zA-Z]+')


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
            data = list(self._get_links(name=dep.base_name))
            cache.dump(data)

        # init releases
        releases = []
        for version, info in data:
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

    def _get_links(self, name: str):
        dep_url = self.url + name
        response = requests.get(dep_url)
        if response.status_code == 404:
            raise PackageNotFoundError(package=name, url=dep_url)
        response.raise_for_status()
        document = html5lib.parse(response.text, namespaceHTMLElements=False)

        for tag in document.findall(".//a"):
            link = tag.get("href")
            if not link:
                continue

            python = tag.get('data-requires-python')
            python = html.unescape(python) if python else '*'
            fragment = parse_qs(urlparse(link).fragment)

            yield dict(url=urljoin(dep_url, link), python=python, digest=fragment.get('sha256'))

    @staticmethod
    def _parse_name(fname: str) -> Tuple[str, str]:
        if fname.endswith('.whl'):
            base = fname.rsplit('-', maxsplit=3)[0]
            name, _, version = base.partition('-')
            return name, version

        base = name.rsplit('.', maxsplit=1)[0]
        parts = base.split('-')
        name = []
        for part in parts:
            if REX_WORD.match(part):
                name.append(part)
            else:
                break
        version = parts[len(name):]
        return '-'.join(name), '-'.join(version)

# built-in
import re
from datetime import datetime
from logging import getLogger
from typing import Dict, Iterable, List, Optional, Tuple, Iterator
from urllib.parse import urlparse, urljoin, parse_qs

# external
import attr
import html
import html5lib
import requests
from dephell_specifier import RangeSpecifier
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

# app
from ...cache import JSONCache
from ...config import config
from ...exceptions import PackageNotFoundError
from ...models.release import Release
from ..base import Interface


logger = getLogger('dephell.repositories.warehouse.simple')
REX_WORD = re.compile('[a-zA-Z]+')


def _process_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname == 'pypi.python.org':
        hostname = 'pypi.org'
    else:
        hostname = parsed.hostname
    if hostname == 'pypi.org' and parsed.path == '/pypi/':
        return parsed.scheme + '://pypi.org/simple/'
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
        links = cache.load()
        if links is None:
            links = list(self._get_links(name=dep.base_name))
            cache.dump(links)

        releases_info = dict()
        for link in links:
            name, version = self._parse_name(link['name'])
            name = canonicalize_name(name)
            if name != dep.name:
                continue
            if not version:
                continue

            if version not in releases_info:
                releases_info[version] = dict(hashes=[], pythons=[])
            if link['digest']:
                releases_info[version]['hashes'].append(link['digest'])
            if link['python']:
                releases_info[version]['pythons'].append(link['python'])

        # init releases
        releases = []
        prereleases = []
        for version, info in releases_info.items():
            # ignore version if no files for release
            release = Release(
                raw_name=dep.raw_name,
                version=version,
                time=datetime(1970, 1, 1, 0, 0),
                python=RangeSpecifier(' || '.join(info['pythons'])),
                hashes=tuple(info['hashes']),
                extra=dep.extra,
            )

            # filter prereleases if needed
            if release.version.is_prerelease:
                prereleases.append(release)
                if not self.prereleases and not dep.prereleases:
                    continue

            releases.append(release)

        # special case for black: if there is no releases, but found some
        # prereleases, implicitly allow prereleases for this package
        if not release and prereleases:
            releases = prereleases

        releases.sort(reverse=True)
        return tuple(releases)

    async def get_dependencies(self, name: str, version: str,
                               extra: Optional[str] = None) -> Tuple[Requirement, ...]:
        ...

    def search(self, query: Iterable[str]) -> List[Dict[str, str]]:
        results = []
        ...
        return results

    def _get_links(self, name: str) -> Iterator[Dict[str, str]]:
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
            parsed = urlparse(link)
            fragment = parse_qs(parsed.fragment)
            yield dict(
                url=urljoin(dep_url, link),
                name=parsed.path.strip('/').split('/')[-1],
                python=html.unescape(python) if python else '*',
                digest=fragment['sha256'][0] if 'sha256' in fragment else None,
            )

    @staticmethod
    def _parse_name(fname: str) -> Tuple[str, str]:
        fname = fname.strip()
        if fname.endswith('.whl'):
            fname = fname.rsplit('-', maxsplit=3)[0]
            name, _, version = fname.partition('-')
            return name, version

        fname = fname.rsplit('.', maxsplit=1)[0]
        if fname.endswith('.tar'):
            fname = fname.rsplit('.', maxsplit=1)[0]
        parts = fname.split('-')
        name = []
        for part in parts:
            if REX_WORD.match(part):
                name.append(part)
            else:
                break
        version = parts[len(name):]
        return '-'.join(name), '-'.join(version)

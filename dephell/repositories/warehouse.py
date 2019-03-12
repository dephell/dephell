# built-in
from urllib.parse import urlparse
from typing import Optional

# external
import attr
import requests
from aiohttp import ClientSession
from packaging.requirements import Requirement

# app
from ..cache import JSONCache, TextCache
from ..config import config
from ..models.author import Author
from ..models.release import Release
from .base import Interface
from ..markers import Markers


def _process_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.path in ('', '/', '/simple', '/simple/'):
        path = '/pypi/'
    else:
        path = parsed.path
    if parsed.hostname == 'pypi.python.org':
        hostname = 'pypi.org'
    else:
        hostname = parsed.hostname
    return parsed.scheme + '://' + hostname + path


@attr.s()
class WareHouseRepo(Interface):
    name = attr.ib(default='pypi')
    url = attr.ib(factory=lambda: config['warehouse'], converter=_process_url)

    hash = None
    link = None

    @staticmethod
    def _update_dep_from_data(dep, data):
        if not dep.description:
            dep.description = data['summary']

        if not dep.authors:
            dep.authors = []
            if data['author']:
                dep.authors.append(Author(name=data['author'], mail=data['author_email']))
            if data['maintainer']:
                dep.authors.append(Author(name=data['maintainer'], mail=data['maintainer_email']))
            dep.authors = tuple(dep.authors)

        if not dep.links:
            if data['project_urls']:
                dep.links = {k.lower(): v for k, v in data['project_urls'].items()}
            if data['package_url'] and data['package_url'] not in dep.links.values():
                dep.links['package'] = data['package_url']
            if data['project_url'] and data['project_url'] not in dep.links.values():
                dep.links['project'] = data['project_url']

        if not dep.classifiers:
            dep.classifiers = tuple(data['classifiers'])

    def get_releases(self, dep) -> tuple:
        # retrieve data
        cache = JSONCache('releases', dep.name)
        data = cache.load()
        if data is None:
            url = '{url}{name}/json'.format(url=self.url, name=dep.name)
            response = requests.get(url)
            if response.status_code == 404:
                raise KeyError('project {name} is not found'.format(name=dep.name))
            data = response.json()
            cache.dump(data)
        elif isinstance(data, str) and data == '':
            return ()

        # update info for dependency
        self._update_dep_from_data(dep=dep, data=data['info'])

        # init releases
        releases = []
        for version, info in data['releases'].items():
            # ignore version if no files for release
            if not info:
                continue
            release = Release.from_response(dep.name, version, info)
            releases.append(release)
        releases.sort(reverse=True)
        return tuple(releases)

    async def get_dependencies(self, name: str, version: str, extra: Optional[str] = None) -> tuple:
        cache = TextCache('deps', name, str(version))
        deps = cache.load()
        if deps is None:
            url = '{url}{name}/{version}/json'.format(
                url=self.url,
                name=name,
                version=version,
            )
            async with ClientSession() as session:
                async with session.get(url) as response:
                    response = await response.json()
            deps = response['info']['requires_dist'] or []
            cache.dump(deps)
        elif deps == ['']:
            return ()

        # filter result
        result = []
        for dep in deps:
            req = Requirement(dep)
            dep_extra = req.marker and Markers(req.marker).extra
            # it's not extra and we want not extra too
            if dep_extra is None and extra is None:
                result.append(req)
                continue
            # it's extra, but we want not the extra
            # or it's not the extra, but we want extra.
            if dep_extra is None or extra is None:
                continue
            # it's extra and we want this extra
            elif dep_extra == extra:
                result.append(req)
                continue

        return tuple(result)

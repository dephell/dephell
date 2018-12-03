# external
import requests
from aiohttp import ClientSession
from packaging.requirements import Requirement

# app
from ..cache import JSONCache, TextCache
from ..models.author import Author
from ..models.release import Release
from .base import Interface


class WareHouseRepo(Interface):
    name = None
    hash = None
    link = None

    def __init__(self, url='https://pypi.org/pypi/'):
        self.url = url

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
            dep.links = {k.lower(): v for k, v in data['project_urls'].items()}
            if data['package_url'] not in dep.links.values():
                dep.links['package'] = data['package_url']
            if data['project_url'] not in dep.links.values():
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
        releases = tuple(releases)

        return releases

    async def get_dependencies(self, name: str, version: str) -> tuple:
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
            # TODO: select right extras
            deps = [dep for dep in deps if 'extra ==' not in dep]
            cache.dump(deps)
        elif deps == ['']:
            return ()
        return tuple(Requirement(dep) for dep in deps)

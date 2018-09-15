import requests
from packaging.requirements import Requirement
from aiohttp import ClientSession

from ..cache import TextCache, JSONCache
from ..models.release import Release


class WareHouseRepo:
    def __init__(self, url='https://pypi.org/pypi/'):
        self.url = url

    def get_releases(self, name: str) -> tuple:
        cache = JSONCache('releases', name)
        data = cache.load()
        if data is None:
            url = "{}{}/json".format(self.url, name)
            response = requests.get(url)
            data = response.json()['releases']
            cache.dump(data)
        elif isinstance(data, str) and data == '':
            return ()

        releases = []
        for version, info in data.items():
            # ignore version if no files for release
            if not info:
                continue
            release = Release.from_response(name, version, info)
            releases.append(release)
        releases.sort(key=lambda release: release.time, reverse=True)
        releases = tuple(releases)

        return releases

    async def get_dependencies(self, name: str, version: str) -> tuple:
        cache = TextCache('deps', name, str(version))
        deps = cache.load()
        if deps is None:
            url = '{}{}/{}/json'.format(self.url, name, version)
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

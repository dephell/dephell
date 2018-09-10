import requests
from packaging.requirements import Requirement

from ..cache import BinCache, TextCache
from ..release import Release


class WareHouseRepo:
    def __init__(self, url='https://pypi.org/pypi/'):
        self.url = url

    def get_releases(self, name):
        cache = BinCache('releases', name)
        data = cache.load()
        if data is not None:
            return data

        url = "{}{}/json".format(self.url, name)
        response = requests.get(url)
        releases = []
        for version, info in response.json()['releases'].items():
            # ignore version if no files for release
            if not info:
                continue
            release = Release.from_response(name, version, info)
            releases.append(release)
        releases.sort(key=lambda release: release.time, reverse=True)
        releases = tuple(releases)

        cache.dump(releases)
        return releases

    def get_dependencies(self, name, version):
        cache = TextCache('deps', self.name, self.version)
        deps = cache.load()
        if deps is None:
            url = '{}{}/{}/json'.format(self.url, name, version)
            response = requests.get(url)
            deps = response.json()['info']['requires_dist'] or []
            # TODO: select right extras
            deps = [dep for dep in deps if 'extra ==' not in dep]
            cache.dump(deps)
        return [Requirement(dep) for dep in deps]

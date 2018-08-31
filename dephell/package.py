import attr
from cached_property import cached_property
from pathlib import Path
import requests
import pickle

from .config import config
from .release import Release
from .utils import check_spec


@attr.s()
class Package:
    name = attr.ib()
    version_spec = attr.ib(converter=str)
    python_spec = attr.ib(converter=str)

    @classmethod
    def from_requirement(cls, req):
        return cls(
            name=req.name,
            version_spec=req.specifier,
            python_spec='',
        )

    def filter_releases(self, releases, spec=None):
        if spec is None:
            spec = self.version_spec
        return set(
            release for release in releases
            if check_spec(release.version, spec)
        )

    @property
    def all_releases(self):
        cache = Path(config['cache_dir']) / 'releases' / self.name
        if cache.exists():
            with cache.open('rb') as stream:
                return pickle.load(stream)

        url = "https://pypi.org/pypi/{}/json".format(self.name)
        response = requests.get(url)
        releases = []
        for version, info in response.json()['releases'].items():
            # ignore version if no files for release
            if not info:
                continue
            release = Release.from_response(self.name, version, info)
            releases.append(release)
        releases.sort(key=lambda r: r.time, reverse=not config['minimal'])
        releases = tuple(releases)

        cache.parent.mkdir(parents=True, exist_ok=True)
        with cache.open('wb') as stream:
            pickle.dump(releases, stream)

        return releases

    @cached_property
    def releases(self):
        return self.filter_releases(self.all_releases)

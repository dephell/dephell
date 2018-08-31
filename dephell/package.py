import attr
from cached_property import cached_property
import requests

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

    @cached_property
    def all_releases(self):
        url = "https://pypi.org/pypi/{}/json".format(self.name)
        response = requests.get(url)
        releases = []
        for version, info in response.json()['releases'].items():
            # ignore version if no files for release
            if not info:
                continue
            release = Release.from_response(self.name, version, info)
            releases.append(release)
        return set(releases)

    @cached_property
    def releases(self):
        return self.filter_releases(self.all_releases)

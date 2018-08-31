from datetime import datetime

import attr
from cached_property import cached_property
from packaging.requirements import Requirement
import requests


@attr.s(hash=False)
class Release:
    name = attr.ib()
    version = attr.ib()
    time = attr.ib(repr=False)
    digest = attr.ib(repr=False)
    python_spec = attr.ib(repr=False)

    @classmethod
    def from_response(cls, name, version, info):
        info = info[-1]
        return cls(
            name=name,
            version=version,
            time=datetime.strptime(info['upload_time'], '%Y-%m-%dT%H:%M:%S'),
            digest=info['digests']['sha256'],
            python_spec=info['requires_python'],
        )

    @cached_property
    def dependencies(self):
        url = 'https://pypi.org/pypi/{}/{}/json'.format(self.name, self.version)
        response = requests.get(url)
        deps = response.json()['info']['requires_dist']
        return [Requirement(dep) for dep in deps]

    def __hash__(self):
        return hash((self.name, self.version))

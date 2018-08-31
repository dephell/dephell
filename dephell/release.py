from datetime import datetime
from pathlib import Path

import attr
from cached_property import cached_property
from packaging.requirements import Requirement
import requests

from .config import config


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
        cache = Path(config['cache_dir']) / 'deps' / self.name / self.version

        if cache.exists():
            with cache.open('r') as stream:
                deps = stream.read()
                if not deps:
                    return []
                deps = deps.split('\n')
        else:
            url = 'https://pypi.org/pypi/{}/{}/json'.format(self.name, self.version)
            response = requests.get(url)
            deps = response.json()['info']['requires_dist'] or []
            # TODO: select right extras
            deps = [dep for dep in deps if 'extra ==' not in dep]

            cache.parent.mkdir(parents=True, exist_ok=True)
            with cache.open('w') as stream:
                stream.write('\n'.join(deps))
        return [Requirement(dep) for dep in deps]

    def __hash__(self):
        return hash((self.name, self.version))

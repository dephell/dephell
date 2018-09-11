from datetime import datetime
import attr
from cached_property import cached_property
from packaging.version import parse


@attr.s()
class Release:
    repo = None

    name = attr.ib()
    version = attr.ib(converter=parse)
    time = attr.ib(repr=False, hash=False)
    # digest = attr.ib(repr=False, hash=False)
    # python_spec = attr.ib(repr=False, hash=False)

    @classmethod
    def from_response(cls, name, version, info):
        info = info[-1]
        return cls(
            name=name,
            version=version,
            time=datetime.strptime(info['upload_time'], '%Y-%m-%dT%H:%M:%S'),
            # digest=info['digests']['sha256'],
            # python_spec=info['requires_python'],
        )

    @cached_property
    def dependencies(self) -> tuple:
        return self.repo.get_dependencies(self.name, self.version)

    def __str__(self):
        return '{}=={}'.format(self.name, self.version)

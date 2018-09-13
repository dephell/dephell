from datetime import datetime
import attr
from cached_property import cached_property
from packaging.utils import canonicalize_name
from packaging.version import parse


@attr.s(hash=False)
class Release:
    dependencies = None

    raw_name = attr.ib()
    version = attr.ib(converter=parse)
    time = attr.ib(repr=False, hash=False)
    # digest = attr.ib(repr=False, hash=False)
    # python_spec = attr.ib(repr=False, hash=False)

    @classmethod
    def from_response(cls, name, version, info):
        info = info[-1]
        return cls(
            raw_name=name,
            version=version,
            time=datetime.strptime(info['upload_time'], '%Y-%m-%dT%H:%M:%S'),
            # digest=info['digests']['sha256'],
            # python_spec=info['requires_python'],
        )

    @cached_property
    def name(self) -> str:
        return canonicalize_name(self.raw_name)

    def __str__(self):
        return '{}=={}'.format(self.raw_name, self.version)

    def hash(self):
        return hash((self.name, self.version))

# built-in
from datetime import datetime
from typing import Optional

# external
import attr
from dephell_specifier import RangeSpecifier
from packaging.utils import canonicalize_name
from packaging.version import parse

# app
from ..cached_property import cached_property


@attr.s(hash=False, eq=False, order=False)
class Release:
    dependencies = None  # type: tuple

    raw_name = attr.ib(type=str)
    version = attr.ib(converter=parse)              # type: ignore
    time = attr.ib(repr=False)                      # upload_time
    python = attr.ib(default=None, repr=False)      # requires_python
    hashes = attr.ib(factory=tuple, repr=False)     # digests/sha256

    extra = attr.ib(type=Optional[str], default=None)

    def __attrs_post_init__(self):
        assert '[' not in self.raw_name, self.raw_name

    @classmethod
    def from_response(cls, name, version, info, extra=None):
        latest = info[-1]
        python = latest['requires_python']
        if python is not None:
            python = RangeSpecifier(python)

        return cls(
            raw_name=name,
            version=version,
            time=datetime.strptime(latest['upload_time'], '%Y-%m-%dT%H:%M:%S'),
            python=python,
            hashes=tuple(rel['digests']['sha256'] for rel in info),
            extra=extra,
        )

    @cached_property
    def name(self) -> str:
        return canonicalize_name(self.raw_name)

    def __hash__(self) -> int:
        return hash((self.name, self.version))

    def __eq__(self, other) -> str:
        if not isinstance(other, type(self)):
            return NotImplemented
        if self.name != other.name:
            return False
        if self.version != other.version:
            return False
        return True

    def __lt__(self, other) -> str:
        if not isinstance(other, type(self)):
            return NotImplemented
        left = (self.name, self.version, self.time)
        right = (other.name, other.version, other.time)
        return left < right

    def __str__(self):
        return '{name}=={version}'.format(name=self.raw_name, version=self.version)

# built-in
from datetime import datetime
from typing import Optional

# external
import attr
from dephell_specifier import RangeSpecifier
from packaging.utils import canonicalize_name
from packaging.version import parse

# app
from ..utils import cached_property


@attr.s(hash=False, cmp=True)
class Release:
    dependencies = None  # type: tuple

    raw_name = attr.ib(type=str, cmp=False)
    version = attr.ib(converter=parse, cmp=True)  # typing: ignore
    time = attr.ib(repr=False, hash=False)                      # upload_time
    python = attr.ib(default=None, repr=False, cmp=False)       # requires_python
    hashes = attr.ib(factory=tuple, repr=False, cmp=False)      # digests/sha256

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

    def __str__(self):
        return '{name}=={version}'.format(name=self.raw_name, version=self.version)

    def hash(self):
        return hash((self.name, self.version))

# external
import attr
from packaging.utils import canonicalize_name

# app
from ..cached_property import cached_property
from .dependency import Dependency
from .groups import Groups


@attr.s(cmp=False)
class ExtraDependency(Dependency):
    extra = attr.ib(type=str, default='')

    def __attrs_post_init__(self):
        assert self.extra != ''

    @classmethod
    def from_dep(cls, dep, extra):
        return cls(**attr.asdict(dep, recurse=False), extra=extra)

    @cached_property
    def groups(self) -> Groups:
        return Groups(dep=self, extra=self.extra)

    @cached_property
    def base_name(self) -> str:
        return canonicalize_name(self.raw_name)

    @cached_property
    def name(self) -> str:
        return '{name}[{extra}]'.format(
            name=self.base_name,
            extra=self.extra,
        )

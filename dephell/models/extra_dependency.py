import attr
from cached_property import cached_property

from .dependency import Dependency
from .groups import Groups


@attr.s()
class ExtraDependency(Dependency):
    extra = attr.ib(type=str, default='')

    @classmethod
    def from_dep(cls, dep, extra):
        return cls(**attr.asdict(dep, recurse=False), extra=extra)

    @cached_property
    def groups(self) -> Groups:
        return Groups(dep=self, extra=self.extra)

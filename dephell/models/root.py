# external
import attr
from cached_property import cached_property
from packaging.utils import canonicalize_name

# app
from .group import Group


@attr.s()
class RootRelease:
    raw_name = attr.ib()
    dependencies = attr.ib(repr=False)

    version = attr.ib(default='1.0')
    time = attr.ib(default=None)

    @cached_property
    def name(self) -> str:
        return canonicalize_name(self.raw_name)

    def __str__(self):
        return self.name


@attr.s()
class RootDependency:
    raw_name = attr.ib(default='root')
    dependencies = attr.ib(factory=list, repr=False)

    repo = None
    applied = False
    locked = False
    compat = True
    used = True

    @cached_property
    def name(self) -> str:
        return canonicalize_name(self.raw_name)

    @cached_property
    def all_releases(self) -> str:
        release = RootRelease(
            raw_name=self.raw_name,
            dependencies=self.dependencies,
        )
        return (release, )

    @cached_property
    def group(self) -> str:
        return Group(number=0, releases=self.all_releases)

    @property
    def groups(self):
        return (self.group, )

    def attach_dependencies(self, dependencies):
        self.dependencies.extend(dependencies)

    def unlock(self):
        raise NotImplementedError

    def merge(self, dep):
        raise NotImplementedError

    def unapply(self, name: str):
        raise NotImplementedError

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{cls}({name})'.format(cls=self.__class__.__name__, name=self.name)

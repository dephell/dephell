from contextlib import suppress
from itertools import dropwhile

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

    version = attr.ib(default='0.0.0')
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

    # additional info strings
    version = attr.ib(default='0.0.0', repr=False)      # Version
    description = attr.ib(default='', repr=False)       # Summary
    license = attr.ib(default='', repr=False)           # License
    long_description = attr.ib(default='', repr=False)  # Description

    # additional info lists
    links = attr.ib(factory=dict, repr=False)           # Home-page, Download-URL
    authors = attr.ib(factory=tuple, repr=False)        # Author, Author-email
    keywords = attr.ib(default=tuple, repr=False)       # Keywords
    classifiers = attr.ib(factory=tuple, repr=False)    # Classifier
    platforms = attr.ib(factory=tuple, repr=False)      # Platform

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
            version=self.version,
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

    @classmethod
    def get_metainfo(cls, other, *others):
        """Merge metainfo, but not dependencies
        """
        merged = attr.asdict(other)
        infos = attr.asdict(others)
        for key, value in merged:
            if value:
                continue
            with suppress(StopIteration):
                merged[key] = next(dropwhile(info[key] for info in infos))
        return cls(**merged)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{cls}({name})'.format(cls=self.__class__.__name__, name=self.name)

# built-in
from contextlib import suppress
from pathlib import Path
from typing import Tuple

# external
import attr
from dephell_discover import Root as PackageRoot
from dephell_specifier import RangeSpecifier
from packaging.utils import canonicalize_name
from packaging.version import parse as parse_version

# app
from ..cached_property import cached_property
from .group import Group
from .author import Author


@attr.s()
class RootRelease:
    raw_name = attr.ib()
    dependencies = attr.ib(repr=False)

    version = attr.ib(default='0.0.0')
    time = attr.ib(default=None)

    extra = None

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

    # additional info lists
    links = attr.ib(factory=dict, repr=False)               # Home-page, Download-URL
    authors = attr.ib(default=tuple(), repr=False)          # Author, Author-email
    keywords = attr.ib(default=tuple(), repr=False)         # Keywords
    classifiers = attr.ib(type=tuple, default=tuple(), repr=False)      # Classifier
    platforms = attr.ib(default=tuple(), repr=False)        # Platform
    entrypoints = attr.ib(default=tuple(), repr=False)      # entry_points

    # additional info objects
    package = attr.ib(default=PackageRoot(Path('.').resolve()), repr=False)  # packages, package_data
    python = attr.ib(default=RangeSpecifier(), repr=False)  # Requires-Python
    readme = attr.ib(default=None, repr=False)              # Description

    repo = None
    applied = False
    locked = False
    compat = True
    used = True
    constraint = None

    @cached_property
    def name(self) -> str:
        return canonicalize_name(self.raw_name)

    @property
    def pep_version(self) -> str:
        """Returns PEP-formatted version
        """
        return str(parse_version(self.version))

    @cached_property
    def all_releases(self) -> Tuple[RootRelease]:
        release = RootRelease(
            raw_name=self.raw_name,
            dependencies=self.dependencies,
            version=self.version,
        )
        return (release, )

    @cached_property
    def group(self) -> Group:
        return Group(number=0, releases=self.all_releases)

    @property
    def groups(self) -> Tuple[Group]:
        return (self.group, )

    @property
    def python_compat(self) -> bool:
        return True

    def attach_dependencies(self, dependencies) -> None:
        self.dependencies.extend(dependencies)

    def unlock(self):
        raise NotImplementedError

    def merge(self, dep):
        raise NotImplementedError

    def unapply(self, name: str):
        raise NotImplementedError

    def copy(self) -> 'RootDependency':
        return type(self)(**attr.asdict(self, recurse=False))

    @classmethod
    def get_metainfo(cls, other, *others) -> 'RootDependency':
        """Merge metainfo, but not dependencies
        """
        merged = attr.asdict(other, recurse=False)
        infos = [attr.asdict(other, recurse=False) for other in others]
        for key, value in merged.items():
            if value:
                continue
            values = (info[key] for info in infos if info[key])
            with suppress(StopIteration):
                merged[key] = next(values)
        root = cls(**merged)

        # get some metainfo from package
        if root.raw_name == 'root' and root.package.packages:
            root.raw_name = root.package.packages[0].module
        info = root.package.metainfo
        if info:
            if root.version == '0.0.0' and info.version:
                root.version = info.version
            if not root.description and info.summary:
                root.description = info.summary
            if not root.license and info.license:
                root.license = info.license
            if not root.authors and info.authors:
                root.authors = tuple(Author.parse(author) for author in info.authors)

        return root

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return '{cls}({name})'.format(cls=self.__class__.__name__, name=self.name)

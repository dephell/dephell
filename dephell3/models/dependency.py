from operator import attrgetter
from collections import defaultdict
import attr
from cached_property import cached_property
from .constraint import Constraint
from .group import Group


@attr.s()
class Dependency:
    repo = None

    name = attr.ib()
    constraint = attr.ib(repr=False)
    applied = attr.ib(default=False)

    # constructors

    @classmethod
    def from_requirement(cls, source, req):
        return cls(
            name=req.name,
            constraint=Constraint(source, req.specifier),
        )

    # properties

    @cached_property
    def normalized_name(self):
        return self.name.lower.replace('_', '-')

    @cached_property
    def all_releases(self):
        return self.repo.get_releases(self.name)

    @cached_property
    def groups(self):
        # group releases by their dependencies
        groups = defaultdict(set)
        for release in self.all_releases:
            key = '|'.join(sorted(map(str, release.dependencies)))
            groups[key].add(release)
        # sort groups by latest release
        groups = sorted(
            groups.values(),
            key=lambda releases: max(releases, key=attrgetter('time')),
            reverse=True,
        )
        # convert every group to Group object
        return [
            Group(releases=releases, number=number)
            for number, releases in enumerate(groups)
        ]

    @cached_property
    def group(self):
        """By first access choose and save best group
        """
        for group in self.groups:
            if not group.empty:
                return group

    @cached_property
    def dependencies(self) -> tuple:
        constructor = self.__class__.from_requirement
        return tuple(constructor(self, req) for req in self.group.dependencies)

    @property
    def locked(self):
        return 'group' in self.__dict__

    @property
    def compat(self):
        # if group has already choosed
        if self.locked:
            return not self.group.empty
        # if group hasn't choosed
        for group in self.groups:
            return bool(self.releases)

    # methods

    def unlock(self):
        del self.__dict__['group']

    def merge(self, dep):
        self.constraint.merge(dep.constraint)
        filtrate = self.constraint.filter
        for group in self.groups:
            group.releases = filtrate(group.all_releases)

    def unapply(self, normalized_name: str):
        self.constraint.unapply(normalized_name)

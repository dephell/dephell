from collections import defaultdict
from operator import attrgetter

import attr
from cached_property import cached_property


@attr.s()
class Node:
    release = attr.id()
    dependency = attr.ib(repr=False)

    layer = attr.ib()  # int, >0, layer number
    applied = attr.ib(default=False)  # True if node's deps applied to graph

    @classmethod
    def from_dependency(cls, dependency):
        return cls(dependency=dependency, release=dependency.best_release)

    @cached_property
    def groups(self):
        groups = defaultdict(set)
        for release in self.dependency.repo.get_releases():
            key = '|'.join(sorted(map(str, release.dependencies)))
            groups[key].add(release)
        # sort groups by latest release
        return sorted(
            groups.values(),
            key=lambda releases: max(releases, key=attrgetter('time')),
            reverse=True,
        )

    def get_group(self, release=None):
        if release is None:
            release = self.release
        for i, group in enumerate(self.groups):
            if release in group:
                return i

    def get_release(self, group):
        group = self.groups[group]
        # sort releases by time
        releases = sorted(
            self.dependency.releases,
            key=attrgetter('time'),
            reverse=True,
        )
        for release in releases:
            if release in group:
                return release

    def __str__(self):
        return self.release.name

    def __hash__(self):
        return hash(self.release.name)

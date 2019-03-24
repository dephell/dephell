# built-in
from operator import attrgetter
from typing import Optional

# app
from ..config import config
from ..utils import cached_property


class Group:
    def __init__(self, number: int, releases: set, dep=None):
        """
        releases (set)
        """
        self.all_releases = self.releases = releases
        self.number = number
        self.dep = dep

    # BEST RELEASE PROPERTIES

    @property
    def best_release(self):
        strategy = max if config['strategy'] == 'max' else min
        best_time = strategy(release.time for release in self.releases)
        best_releases = [release for release in self.releases if release.time == best_time]
        if len(best_releases) == 1:
            return best_releases[0]
        return strategy(self.releases, key=attrgetter('version'))

    @property
    def time(self):
        return self.best_release.time

    # RANDOM RELEASE PROPERTIES

    @cached_property
    def random(self):
        return next(iter(self.all_releases))

    @cached_property
    def raw_name(self) -> str:
        return self.random.raw_name

    @cached_property
    def name(self) -> str:
        return self.random.name

    @property
    def extra(self) -> Optional[str]:
        return self.random.extra

    # OTHER PROPERTIES

    @cached_property
    def metadependency(self):
        """MetaDependency is a dependency on the parent for extra.

        For example, `requests[security]` extra depends on `requests` Dependency.
        """
        if self.extra is None:
            raise ValueError('metadependency available only for group of extras')
        if self.dep is None:
            raise ValueError('dep required for group of extras')
        min_version = min(self.versions)
        max_version = max(self.versions)
        from ..controllers import DependencyMaker
        return DependencyMaker.from_requirement(
            source=self.dep,
            req='{name}>={min_version},<={max_version}'.format(
                name=self.raw_name,
                min_version=min_version,
                max_version=max_version,
            ),
        )[0]

    @property
    def dependencies(self) -> tuple:
        deps = self.random.dependencies
        if self.extra is not None:
            deps += (self.metadependency, )
        return deps

    @cached_property
    def versions(self) -> set:
        return {release.version for release in self.all_releases}

    @property
    def empty(self) -> bool:
        return not bool(self.releases)

    def __str__(self):
        versions = sorted(release.version for release in self.releases)
        versions = [str(v) for v in versions]
        if not versions:
            versions = '[EMPTY]'
        elif len(versions) == 1:
            versions = '==' + versions[0]
        elif len(versions) <= 4:
            versions = '({versions})'.format(versions=', '.join(versions))
        else:
            versions = '({first}–{last})'.format(first=versions[0], last=versions[-1])
        return '{name}{versions}'.format(name=self.name, versions=versions)

    def __repr__(self):
        return 'Group({info})'.format(info=str(self))

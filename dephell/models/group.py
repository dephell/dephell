# built-in
from operator import attrgetter

# external
from cached_property import cached_property

# app
from ..config import config


class Group:
    def __init__(self, number, releases):
        """
        releases (set)
        """
        self.all_releases = self.releases = releases
        self.number = number

    @property
    def best_release(self):
        strategy = max if config['strategy'] == 'max' else min
        best_time = strategy(release.time for release in self.releases)
        best_releases = [release for release in self.releases if release.time == best_time]
        if len(best_releases) == 1:
            return best_releases[0]
        return strategy(self.releases, key=attrgetter('version'))

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
    def dependencies(self) -> tuple:
        return self.random.dependencies

    @property
    def empty(self) -> bool:
        return not bool(self.releases)

    @property
    def time(self):
        return self.best_release.time

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

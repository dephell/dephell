from operator import attrgetter
from cached_property import cached_property


class Group:
    def __init__(self, number, releases):
        """
        releases (set)
        """
        self.all_releases = self.releases = releases
        self.number = number

    @property
    def best_release(self):
        best_time = max(release.time for release in self.releases)
        best_releases = [release for release in self.releases if release.time == best_time]
        if len(best_releases) == 1:
            return best_releases[0]
        return max(self.releases, key=attrgetter('version'))

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
            versions = '({})'.format(', '.join(versions))
        else:
            versions = '({}–{})'.format(versions[0], versions[-1])
        return '{}{}'.format(self.name, versions)

    def __repr__(self):
        return 'Group({})'.format(str(self))

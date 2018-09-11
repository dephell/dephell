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
        return max(self.releases, key=attrgetter('time'))

    @cached_property
    def random(self):
        return next(iter(self.all_releases))

    @cached_property
    def name(self) -> str:
        return self.random.name

    @cached_property
    def normalized_name(self):
        return self.name.lower.replace('_', '-')

    @property
    def empty(self) -> bool:
        return bool(self.releases)

    @property
    def time(self):
        return self.best_release.time

    def __str__(self):
        versions = sorted(release.version for release in self.releases)
        if len(versions) < 10:
            versions = ', '.join(versions)
        else:
            versions = '{}, ..., {}'.format(versions[0], versions[-1])
        return '{} ({})'.format(self.name, versions)

    def __repr__(self):
        return 'Group({})'.format(str(self))

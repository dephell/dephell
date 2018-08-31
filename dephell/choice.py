import attr
from cached_property import cached_property


@attr.s(hash=False)
class Choice:
    package = attr.ib()
    release = attr.ib()

    @cached_property
    def distance(self):
        latest = max(self.package.all_releases, key=lambda release: release.time)
        delta = latest.time - self.release.time
        return delta.days

    def __hash__(self):
        return hash(self.release)

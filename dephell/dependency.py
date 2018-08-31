import attr
from cached_property import cached_property


@attr.s()
class Dependency:
    package = attr.ib()
    version_spec = attr.ib()
    python_spec = attr.ib()

    @classmethod
    def from_package(cls, package, release=None):
        self = cls(
            package=package,
            version_spec=package.version_spec,
            python_spec=package.python_spec,
        )
        if release is not None:
            self.releases = {release}
        return self

    @cached_property
    def releases(self):
        return self.package.filter_releases(self.package.all_releases, self.version_spec)

    @cached_property
    def best_release(self):
        """Latest release from allowed in spec
        """
        return max(self.package.releases, key=lambda release: release.time)

    def __and__(self, other):
        if other.package != self.package:
            raise NotImplementedError
        new = self.__class__(
            package=self.package,
            version_spec=','.join(self.version_spec, other.version_spec),
            python_spec=','.join(self.python_spec, other.python_spec),
        )
        new.releases = self.releases & other.releases
        return new

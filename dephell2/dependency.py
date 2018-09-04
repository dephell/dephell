import attr
from cached_property import cached_property

from .utils import check_spec


@attr.s()
class Dependency:
    repo = None

    name = attr.ib(convert=lambda name: name.lower.replace('_', '-'))
    # versions specify mapping of specs by source of constraint
    # versions[name][version] = spec
    versions = attr.ib()

    # constructors

    @classmethod
    def from_requirement(cls, source, req):
        return cls(
            name=req.name,
            versions={source.name: {source.version: req.specifier}},
        )

    # properties

    @cached_property
    def spec(self):
        specs = (spec for specs in self.versions.values() for spec in specs.values())
        return ','.join(specs)

    @cached_property
    def releases(self):
        return set(
            release for release in self.repo.get_releases()
            if check_spec(release.version, self.spec)
        )

    @cached_property
    def best_release(self):
        """Latest release from allowed in spec
        """
        return max(self.package.releases, key=lambda release: release.time)

    @property
    def compat(self):
        return bool(self.releases)

    # methods

    def reset(self):
        for name in ('spec', 'releases', 'best_release'):
            if name in self.__dict__:
                del self.__dict__[name]

    # magic methods

    def __str__(self):
        return '{}{}'.format(self.package.name, self.version_spec)

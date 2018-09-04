import attr
from cached_property import cached_property
from collections import namedtuple

from .utils import check_spec


Spec = namedtuple('Spec', ['version', 'spec'])


@attr.s()
class Dependency:
    repo = None

    name = attr.ib()
    # versions specify mapping of specs by source of constraint
    # versions[name] = Spec(version, spec)
    versions = attr.ib()

    # constructors

    @classmethod
    def from_requirement(cls, source, req):
        return cls(
            name=req.name,
            versions={source.normalized_name: Spec(source.version, str(req.specifier))},
        )

    # properties

    @cached_property
    def normalized_name(self):
        return self.name.lower.replace('_', '-')

    @cached_property
    def spec(self):
        return ','.join(spec.spec for spec in self.versions.values())

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

    def apply(self, dep, spec):
        self.unapply(dep.normalized_name)
        self.versions[dep.normalized_name] = Spec(dep.version, str(spec))
        self.reset()

    def unapply(self, normalized_name):
        if normalized_name not in self.versions:
            return
        del self.versions[normalized_name]
        self.reset()

    # magic methods

    def __str__(self):
        return '{}{}'.format(self.name, self.spec)

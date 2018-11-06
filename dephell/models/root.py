import attr

from .group import Group


@attr.s()
class RootRelease:
    name = attr.ib()
    dependencies = attr.ib()

    version = attr.ib(default='1.0')
    time = attr.ib(default='')

    @property
    def raw_name(self):
        return self.name

    def __str__(self):
        return self.name


class RootDependency:
    repo = None
    applied = False
    locked = False
    compat = True
    used = True

    def __init__(self, name: str='root'):
        self.name = name
        self.raw_name = name.title()

        self.dependencies = []
        self.all_releases = (RootRelease(
            name=name,
            dependencies=self.dependencies,
        ), )
        self.group = Group(number=0, releases=self.all_releases)
        self.groups = (self.group, )

    def attach_dependencies(self, dependencies):
        self.dependencies.extend(dependencies)

    def unlock(self):
        raise NotImplementedError

    def merge(self, dep):
        raise NotImplementedError

    def unapply(self, name: str):
        raise NotImplementedError

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

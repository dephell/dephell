from .group import Group


class RootRelease:
    raw_name = 'root'
    version = ''
    time = ''

    def __init__(self, dependencies):
        self.dependencies = dependencies

    def __str__(self):
        return 'root'


class RootDependency:
    repo = None
    raw_name = 'ROOT'
    name = 'root'
    applied = False
    locked = False
    compat = True

    def __init__(self):
        self.dependencies = []
        self.all_releases = (RootRelease(self.dependencies), )
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
        return 'root'

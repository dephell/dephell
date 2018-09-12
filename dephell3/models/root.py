from .group import Group


class RootRelease:
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

    def __init__(self, dependencies):
        self.dependencies = dependencies
        self.all_releases = (RootRelease(dependencies), )
        self.group = Group(number=0, releases=self.all_releases)
        self.groups = (self.group, )

    def unlock(self):
        raise NotImplementedError

    def merge(self, dep):
        raise NotImplementedError

    def unapply(self, name: str):
        raise NotImplementedError

    def __str__(self):
        return 'root'

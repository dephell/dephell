from datetime import datetime
from .dependency import Dependency


class RootRelease:
    name = 'root'
    version = '0.0.0'

    def __init__(self, dependencies):
        self.dependencies = dependencies
        self.time = datetime.now()

    def __str__(self):
        return 'root'


class RootDependency:
    repo = None
    name = 'root'
    versions = None
    compat = True

    def __init__(self, dependencies):
        self._dependencies = dependencies

    @property
    def normalized_name(self):
        return self.name

    @property
    def releases(self):
        return {RootRelease(self._dependencies)}

from .dependency import Dependency
from .release import Release
from .repositories import WareHouseRepo


Dependency.repo = WareHouseRepo()
Release.repo = WareHouseRepo()


class Resolver:
    def __init__(self, deps):
        self.graph = dict()
        for dep in deps:
            self.graph[dep.normalized_name] = dep

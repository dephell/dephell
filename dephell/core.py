from collections import OrderedDict
from itertools import product

from pip._internal.download import PipSession
from pip._internal.req import parse_requirements

from .choice import Choice
from .dependency import Dependency
from .package import Package


class Resolver:
    def __init__(self, packages):
        self.packages = packages
        self._packages_cache = packages.copy()

    @classmethod
    def from_requirements(cls, path):
        packages = []
        for req in parse_requirements(str(path), session=PipSession()):
            packages.append(Package.from_requirement(req.req))
        return cls(packages)

    @property
    def combinations(self):
        choices = []
        for package in self.packages:
            combination = []
            for release in package.releases:
                choice = Choice(package=package, release=release)
                combination.append(choice)
            choices.append(combination)
        combinations = list(product(*choices))
        combinations.sort(key=lambda choices: sum(choice.distance for choice in choices))
        return combinations

    def get_deps(self, dep):
        release = dep.best_release
        deps = {dep.package.name: dep}
        for subdep in release.dependencies:
            # get package
            package = self._packages_cache.get(subdep.name)
            if package is None:
                package = Package(
                    name=subdep.name,
                    version_spec='',
                    python_spec='',
                )
                self._packages_cache[package.name] = package

            # get dep
            subdep = Dependency(
                package=package,
                version_spec=dep.specifier,
                python_spec='',
            )

            # try merge this dep with other deps
            if package.name in deps:
                deps[package.name] &= subdep
                if not deps[package.name].releases:
                    return
            else:
                deps[package.name] = subdep

    def build_graph(self, choices):
        graph = dict()
        # get first-level dependencies
        for choice in choices:
            dep = Dependency(
                package=choice.package,
                release=choice.release,
            )
            deps = self.get_deps(dep)
            # if cannot resolve conflicts
            if deps is None:
                return

            # add deps to graph
            for name, dep in deps.items():
                if name not in graph:
                    graph[name] = dep
                    continue
                graph[name] &= dep
                # if cannot resolve conflicts
                if not graph[name].releases:
                    return

        return graph

    @staticmethod
    def sort_graph(graph):
        return OrderedDict(sorted(list(graph.items())))

    def resolve(self):
        for choices in self.combinations:
            graph = self.build_graph(choices)
            if graph is None:
                continue
            self.graph = self.sort_graph(graph)
            return self
        raise ImportError('Can not resolve dependencies')

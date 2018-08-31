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

    def build_graph(self, choices):
        graph = dict()
        # get first-level dependencies
        for choice in choices:
            dep = Dependency(
                package=choice.package,
                release=choice.release,
            )
            graph[choice.package.name] = dep
        ...
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

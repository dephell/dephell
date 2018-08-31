from logging import getLogger
from collections import OrderedDict
from itertools import product, islice

from pip._internal.download import PipSession
from pip._internal.req import parse_requirements

from .choice import Choice
from .config import config
from .dependency import Dependency
from .package import Package


logger = getLogger(__name__)


class Resolver:
    def __init__(self, packages):
        self.packages = packages
        self._packages_cache = {package.name: package for package in packages}
        self._deps_log = set()

    # constructors

    @classmethod
    def from_requirements(cls, path):
        packages = []
        for req in parse_requirements(str(path), session=PipSession()):
            packages.append(Package.from_requirement(req.req))
        return cls(packages)

    # dumpers

    def to_requirements(self, path=None):
        lines = []
        for dep in self.graph.values():
            line = '{name}=={version}'.format(
                name=dep.best_release.name,
                version=dep.best_release.version,
            )
            lines.append(line)
        content = '\n'.join(lines) + '\n'
        if path is None:
            return content
        with open(str(path), 'w') as stream:
            stream.write(content)

    # other

    def get_combinations(self):
        choices = []
        for package in self.packages:
            combination = []
            for release in islice(package.releases, 0, config['releases_limit']):
                choice = Choice(package=package, release=release)
                combination.append(choice)
            choices.append(combination)
        combinations = product(*choices)
        if config['sort']:
            combinations = list(combinations)
            combinations.sort(key=lambda choices: sum(choice.distance for choice in choices))
        return islice(combinations, 0, config['choices_limit'])

    def get_deps(self, dep):
        release = dep.best_release
        all_deps = [(dep.package.name, dep)]

        # avoid dependencies recursion
        digest = ''.join([dep.package.name, dep.package.version_spec])
        if digest in self._deps_log:
            return dict(all_deps)
        self._deps_log.add(digest)

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
                version_spec=subdep.specifier,
                python_spec='',
            )

            if subdep.package.name == dep.package.name:
                logger.warning('{} depends on itself'.format(dep.package.name))

            # save this deps to list
            subdeps = self.get_deps(subdep)
            if not subdeps:
                return
            all_deps.extend(list(subdeps.items()))

        # collect all deps to one mapping
        deps = {}
        for name, subdep in all_deps:
            if name not in deps:
                deps[name] = subdep
                continue
            # try merge this dep with other deps
            deps[name] &= subdep
            if not deps[name].releases:
                logger.warning('no compat releases for {}'.format(subdep))
                return
        return deps

    def build_graph(self, choices):
        graph = dict()
        # get first-level dependencies
        for choice in choices:
            dep = Dependency.from_package(
                package=choice.package,
                release=choice.release,
            )
            deps = self.get_deps(dep)
            # if cannot resolve conflicts
            if deps is None:
                logger.warning('no resolved deps for {}'.format(dep))
                return

            # add deps to graph
            for name, dep in deps.items():
                if name not in graph:
                    graph[name] = dep
                    continue
                graph[name] &= dep
                # if cannot resolve conflicts
                if not graph[name].releases:
                    logger.warning('cannot resolve {}'.format(dep))
                    return

        return graph

    @staticmethod
    def sort_graph(graph):
        return OrderedDict(sorted(list(graph.items())))

    def resolve(self):
        for choices in self.get_combinations():
            logger.warning("Try combination...")
            graph = self.build_graph(choices)
            if graph is None:
                continue
            self.graph = self.sort_graph(graph)
            return self
        raise ImportError('Can not resolve dependencies')

# built-in
from collections import OrderedDict, defaultdict
from typing import Iterable, Optional, Set, Tuple

# app
from ..cached_property import cached_property


class Requirement:
    _properties = (
        'name', 'release', 'version', 'extras', 'markers',
        'hashes', 'sources', 'editable', 'git', 'rev',
        'description', 'optional', 'platform', 'python',
    )

    def __init__(self, dep, lock: bool, roots: Iterable[str] = None):
        self.dep = dep
        self.lock = lock
        self.extra_deps = tuple()
        self._roots = set(roots or [])

    @classmethod
    def from_graph(cls, graph, *, lock: bool) -> Tuple['Requirement', ...]:
        result = OrderedDict()
        extras = defaultdict(list)
        applied = graph.applied
        roots = [root.name for root in graph.get_layer(0)]

        # if roots wasn't applied then apply them
        if len(graph._layers) == 1:
            for root in graph._roots:
                for dep in root.dependencies:
                    graph.add(dep)

        # get all nodes
        for layer in reversed(graph._layers[1:]):  # skip roots
            for dep in sorted(layer):
                if applied and not dep.applied:
                    continue
                if dep.constraint.empty:
                    continue
                if dep.extra is None:
                    req = cls(dep=dep, lock=lock, roots=roots)
                    result[dep.name] = req
                else:
                    extras[dep.base_name].append(dep)

        # add extras
        for name, deps in extras.items():
            if name not in result and name in roots:
                continue
            result[name].extra_deps = tuple(sorted(deps, key=lambda dep: dep.extra))
        return tuple(result.values())

    @cached_property
    def release(self):
        if self.lock:
            return self.dep.group.best_release

    @cached_property
    def dependencies(self) -> tuple:
        extra_deps = sum([dep.dependencies for dep in self.extra_deps], tuple())
        return self.dep.dependencies + extra_deps

    @property
    def editable(self) -> Optional[bool]:
        if self.dep.editable:
            return True
        return None  # mypy wants it

    @property
    def prereleases(self) -> Optional[bool]:
        if self.dep.prereleases:
            return True
        return None  # mypy wants it

    @property
    def link(self):
        return self.dep.link

    @property
    def git(self) -> Optional[str]:
        if getattr(self.dep.link, 'vcs', '') == 'git':
            return self.dep.link.short
        return None  # mypy wants it

    @property
    def rev(self) -> Optional[str]:
        return getattr(self.dep.link, 'rev', None) or None

    @property
    def name(self) -> str:
        return self.dep.name

    @cached_property
    def raw_name(self) -> str:
        """Like .name, but saves dots.

        `.name` replaces `.` by `-`, but setuptools fails on it.
        """
        return self.dep.raw_name.replace('_', '-').lower()

    @property
    def description(self) -> str:
        return self.dep.description

    @cached_property
    def version(self) -> Optional[str]:
        if self.link:
            return None  # mypy wants it
        if self.lock:
            return '==' + str(self.release.version)

        constraint = self.dep.constraint.copy()
        # drop all constraints not from roots
        if self._roots:
            for name in (constraint.sources - self._roots):
                constraint.unapply(name)
        return str(constraint)

    @cached_property
    def extras(self) -> Tuple[str, ...]:
        return tuple(dep.extra for dep in self.extra_deps)

    @property
    def markers(self) -> Optional[str]:
        markers = self.dep.marker
        if markers:
            return str(markers)
        return None  # mypy wants it

    @cached_property
    def platform(self) -> Optional[str]:
        for marker in ('sys_platform', 'platform_system', 'os_name'):
            platform = self.dep.marker.get_string(marker)
            if platform:
                return platform

    @cached_property
    def python(self) -> Optional[str]:
        python = self.dep.marker.python_version
        if python:
            return str(python)
        return None

    @cached_property
    def hashes(self) -> Optional[tuple]:
        if not self.lock:
            return None  # mypy wants it

        hashes = set()
        for digest in self.release.hashes:
            if ':' not in digest:
                digest = 'sha256:' + digest
            hashes.add(digest)

        if not hashes:
            # TODO: calculate hash for local data
            ...

        return tuple(sorted(hashes))

    @cached_property
    def sources(self) -> tuple:
        """List of parent packages that depends on this package.
        """
        return tuple(sorted(self.dep.constraint.sources))

    # envs

    @property
    def is_main(self) -> bool:
        """
        For poetry and Pipfile it means that dependency placed in the main section.
        """
        return 'main' in self.dep.envs

    @property
    def main_envs(self) -> Set[str]:
        """
        For setup.py, egg-info and other classic things it returns all extras
        for dependency including `dev`.
        """
        return self.dep.envs - {'main'}

    @property
    def is_dev(self) -> bool:
        """
        For poetry and Pipfile it means that dependency placed in the dev section.
        """
        return 'dev' in self.dep.envs

    @property
    def dev_envs(self) -> Set[str]:
        """
        For poetry it returns extras for dependencies in the dev section.
        """
        return self.dep.envs - {'dev'}

    @property
    def optional(self) -> bool:
        """
        Required for poetry. Shows that req has some extras except dev or main.
        In poetry it has quite different meaning, but let's think about it in this way.
        """
        # install everything on dev environment
        if 'dev' in self.dep.envs:
            return False
        return bool(self.dep.envs - {'dev', 'main'})

    # magic methods

    def __iter__(self):
        for name in self._properties:
            value = getattr(self, name)
            if value:
                yield name, value

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return '{name}({dep}, lock={lock})'.format(
            name=self.__class__.__name__,
            dep=self.name,
            lock=self.lock,
        )

    def __lt__(self, other: 'Requirement') -> bool:
        return self.name < other.name

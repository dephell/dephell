
from collections import OrderedDict, defaultdict
from typing import Optional, Set, Tuple

# app
from ..utils import cached_property


class Requirement:
    _properties = (
        'name', 'release', 'version', 'extras', 'markers',
        'hashes', 'sources', 'editable', 'git', 'rev',
        'description', 'optional',
    )

    def __init__(self, dep, lock: bool):
        self.dep = dep
        self.lock = lock
        self.extra_deps = tuple()

    @classmethod
    def from_graph(cls, graph, *, lock: bool) -> Tuple['Requirement', ...]:
        result = OrderedDict()
        extras = defaultdict(list)
        applied = graph.applied

        # if roots wasn't applied then apply them
        if len(graph._layers) == 1:
            for root in graph._layers[0]:
                for dep in root.dependencies:
                    graph.add(dep)

        # get all nodes
        for layer in reversed(graph._layers[1:]):  # skip roots
            for dep in sorted(layer):
                if applied and not dep.applied:
                    continue
                if dep.extra is None:
                    req = cls(dep=dep, lock=lock)
                    result[dep.name] = req
                else:
                    extras[dep.base_name].append(dep)

        # add extras
        for name, deps in extras.items():
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
    def link(self):
        return self.dep.link

    @property
    def envs(self) -> Set[str]:
        return self.dep.envs

    @property
    def optional(self) -> bool:
        return bool(self.dep.envs)

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

    @property
    def description(self) -> str:
        return self.dep.description

    @property
    def version(self) -> Optional[str]:
        if self.link:
            return None  # mypy wants it
        if self.lock:
            return '==' + str(self.release.version)
        return str(self.dep.constraint)

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
        return tuple(sorted(self.dep.constraint.sources))

    # magic methods

    def __iter__(self):
        for name in self._properties:
            value = getattr(self, name)
            if value:
                yield name, value

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{name}({dep}, lock={lock})'.format(
            name=self.__class__.__name__,
            dep=self.name,
            lock=self.lock,
        )

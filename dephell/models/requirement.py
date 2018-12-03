# built-in
from typing import Optional

# external
from cached_property import cached_property


class Requirement:
    _properties = (
        'name', 'release', 'version', 'extras', 'markers',
        'hashes', 'sources', 'editable',
    )

    def __init__(self, dep, lock: bool):
        self.dep = dep
        self.lock = lock

    @classmethod
    def from_graph(cls, graph, *, lock: bool) -> tuple:
        result = []
        applied = graph.applied
        if len(graph._layers) == 1:
            for root in graph._layers[0]:
                for dep in root.dependencies:
                    graph.add(dep)
        for layer in graph._layers[1:]:  # skip roots
            for dep in sorted(layer):
                if not applied or dep.applied:
                    req = cls(dep=dep, lock=lock)
                    result.append(req)
        return tuple(result)

    @cached_property
    def release(self):
        if self.lock:
            return self.dep.group.best_release

    @property
    def editable(self) -> Optional[bool]:
        if self.dep.editable:
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
        return getattr(self.dep.link, 'rev', None)

    @property
    def name(self) -> str:
        return self.dep.name

    @property
    def version(self) -> Optional[str]:
        if self.link:
            return None  # mypy wants it
        if self.lock:
            return '==' + str(self.release.version)
        return str(self.dep.constraint)

    @cached_property
    def extras(self) -> tuple:
        return tuple(sorted(self.dep.extras))

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

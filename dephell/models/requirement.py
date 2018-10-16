from cached_property import cached_property


class Requirement:
    _properties = (
        'name', 'release', 'version', 'extras', 'markers',
        'hashes', 'sources',
    )

    def __init__(self, dep, lock: bool):
        self.dep = dep
        self.lock = lock

    @cached_property
    def release(self):
        if self.lock:
            return self.dep.group.best_release

    @property
    def name(self) -> str:
        return self.dep.name

    @property
    def version(self) -> str:
        if self.lock:
            return '==' + str(self.release.version)
        return str(self.dep.constraint)

    @cached_property
    def extras(self) -> tuple:
        return tuple(sorted(self.dep.extras))

    @property
    def markers(self) -> str:
        return str(self.dep.marker)

    @cached_property
    def hashes(self) -> tuple:
        if not self.lock:
            return

        hashes = set()
        for digest in self.release.hashes:
            if ':' not in digest:
                digest = 'sha256:' + digest
            hashes.add(digest)

        if not hashes:
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

# built-in
from copy import deepcopy

# external
from dephell_specifier import RangeSpecifier


class Constraint:
    def __init__(self, source, spec):
        """
        source (Dependency)
        spec (str, LegacySpecifier, Specifier)
        """
        self._specs = {source.name: RangeSpecifier(spec)}
        self._groups = {source.name: source.group.number}

    # properties

    @property
    def empty(self) -> bool:
        return not bool(self._specs)

    @property
    def sources(self) -> set:
        return set(self._specs.keys())

    @property
    def specs(self) -> tuple:
        result = []
        for name, spec in self._specs.items():
            result.append((name, str(spec)))
        return tuple(sorted(result))

    # methods

    def attach_time(self, releases) -> None:
        """Attach time to all specifiers if possible
        """
        for spec in self._specs.values():
            spec.attach_time(releases)

    def apply(self, dep, spec) -> None:
        if dep.name in self._groups:
            # don't apply same group twice
            if self._groups[dep.name] == dep.group.number:
                return
            # unapply old group of this package:
            self.unapply(dep.name)
        # save params
        self._specs[dep.name] = RangeSpecifier(spec)
        self._groups[dep.name] = dep.group.number

    def unapply(self, name: str) -> None:
        if name not in self._specs:
            return
        del self._specs[name]
        del self._groups[name]

    def filter(self, releases) -> set:
        """Filter releases
        """
        result = set()
        for release in releases:
            for spec in self._specs.values():
                if release not in spec:
                    break
            else:
                result.add(release)
        return result

    def copy(self) -> 'Constraint':
        return deepcopy(self)

    # magic methods

    def __and__(self, other):
        return self.copy().__iand__(other)

    def __iand__(self, other):
        if not isinstance(other, Constraint):
            return NotImplemented
        for name, group in other._groups.items():
            # if group already applied
            # if self._groups.get(name, -1) == group:
            #     continue
            self._groups[name] = group

            spec = other._specs[name]
            if name in self._specs:
                self._specs[name] += spec
            else:
                self._specs[name] = spec
        return self

    def __or__(self, other):
        return self.copy().__ior__(other)

    def __ior__(self, other):
        if not isinstance(other, Constraint):
            return NotImplemented
        for name, group in other._groups.items():
            self._groups[name] = group
            spec = other._specs[name]
            if name in self._specs:
                self._specs[name] = RangeSpecifier(str(self._specs[name]) + '||' + str(spec))
            else:
                self._specs[name] = spec
        return self

    def __str__(self) -> str:
        specs = map(str, set(self._specs.values()))
        return ','.join(spec for spec in sorted(specs) if spec)

    def __repr__(self) -> str:
        return '{name}({specs})'.format(
            name=type(self).__name__,
            specs=str(self),
        )

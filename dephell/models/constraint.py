
from copy import deepcopy


from dephell_specifier import RangeSpecifier


class Constraint:
    def __init__(self, source, spec):
        """
        source (Dependency)
        spec (str, LegacySpecifier, Specifier)
        """
        self._specs = {source.name: RangeSpecifier(spec)}
        self._groups = {source.name: source.group.number}

    def attach_time(self, releases) -> None:
        """Attach time to all specifiers if possible
        """
        for spec in self._specs.values():
            spec.attach_time(releases)

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

    def apply(self, dep, spec):
        if dep.name in self._groups:
            # don't apply same group twice
            if self._groups[dep.name] == dep.group.number:
                return
            # unapply old group of this package:
            self.unapply(dep.name)
        # save params
        self._specs[dep.name] = RangeSpecifier(spec)
        self._groups[dep.name] = dep.group.number

    def merge(self, constraint):
        for name, group in constraint._groups.items():
            # if group already applied
            # if self._groups.get(name, -1) == group:
            #     continue
            self._groups[name] = group

            spec = constraint._specs[name]
            if name in self._specs:
                self._specs[name] += spec
            else:
                self._specs[name] = spec

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

    def copy(self):
        return deepcopy(self)

    def __str__(self):
        specs = map(str, self._specs.values())
        specs = sorted(specs)
        return ','.join(specs)

    def __repr__(self):
        return '{name}({specs})'.format(
            name=type(self).__name__,
            specs=str(self),
        )

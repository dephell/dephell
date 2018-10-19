from itertools import chain
from packaging.specifiers import LegacySpecifier, Specifier, InvalidSpecifier
from packaging.version import LegacyVersion
from copy import deepcopy


class Constraint:
    def __init__(self, source, spec):
        """
        source (Dependency)
        spec (str, LegacySpecifier, Specifier)
        """
        self._specs = {source.name: self._make_spec(spec)}
        self._groups = {source.name: source.group.number}

    @staticmethod
    def _make_spec(spec) -> set:
        if not isinstance(spec, (list, tuple)):
            spec = str(spec).split(',')
        result = set()
        for constr in spec:
            if constr in ('', '*'):
                continue
            try:
                result.add(Specifier(constr))
            except InvalidSpecifier:
                result.add(LegacySpecifier(constr))
        return result

    @staticmethod
    def _check(version, spec) -> bool:
        """
        https://www.python.org/dev/peps/pep-0440/
        """
        if not spec:
            return True

        legacy_version = isinstance(version, LegacyVersion)
        legacy_spec = isinstance(version, LegacySpecifier)

        # version and spec both legacy or semantic at the same time
        if legacy_version == legacy_spec:
            return version in spec

        # make both legacy
        if not legacy_version:
            version = LegacyVersion(version)
        if not legacy_spec:
            spec = LegacySpecifier(str(spec))

        # check legacy version
        return version in spec

    @property
    def empty(self) -> bool:
        return not bool(self._specs)

    @property
    def sources(self) -> set:
        return set(self._specs.keys())

    def apply(self, dep, spec):
        if dep.name in self._groups:
            # don't apply same group twice
            if self._groups[dep.name] == dep.group.number:
                return
            # unapply old group of this package:
            self.unapply(dep.name)
        # save params
        self._specs[dep.name] = self._make_spec(spec)
        self._groups[dep.name] = dep.group.number

    def merge(self, constraint):
        for name, group in constraint._groups.items():
            # if group already applied
            # if self._groups.get(name, -1) == group:
            #     continue
            self._groups[name] = group

            spec = constraint._specs[name]
            if name in self._specs:
                self._specs[name].update(spec)
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
            for spec in chain(*self._specs.values()):
                if not self._check(version=release.version, spec=spec):
                    break
            else:
                result.add(release)
        return result

    def copy(self):
        return deepcopy(self)

    def __str__(self):
        specs = map(str, chain(*self._specs.values()))
        specs = sorted(specs)
        return ','.join(specs)

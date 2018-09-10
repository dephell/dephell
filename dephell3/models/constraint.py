from itertools import chain
from packaging.specifiers import LegacySpecifier, Specifier, InvalidSpecifier
from packaging.version import LegacyVersion


class Constraint:
    def __init__(self, source, spec):
        """
        source (Dependency)
        spec (str, LegacySpecifier, Specifier)
        """
        self._specs = {source.normalized_name: self._make_spec(spec)}
        self._groups = {source.normalized_name: source.group.number}

    @staticmethod
    def _make_spec(self, spec):
        if not isinstance(spec, (list, tuple)):
            spec = str(spec).split(',')
        result = []
        for constr in spec:
            try:
                result.append(Specifier(spec))
            except InvalidSpecifier:
                result.append(LegacySpecifier(spec))
        return result

    @staticmethod
    def _check(version, spec):
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
            version = LegacySpecifier(version)

        # check legacy version
        return version in spec

    def apply(self, dep, spec):
        if dep.normalized_name in self._groups:
            # don't apply same group twice
            if self._groups[dep.normalized_name] == dep.group.number:
                return
            # unapply old group of this package:
            self.unapply(dep)
        # save params
        self._specs[dep.normalized_name] = self._make_spec(spec)
        self._groups[dep.normalized_name] = dep.group.number

    def unapply(self, dep):
        if dep.normalized_name not in self._specs:
            return
        del self._specs[dep.normalized_name]
        del self._groups[dep.normalized_name]

    def filter(self, releases):
        """Filter releases
        """
        result = {}
        for release in releases:
            for spec in chain(*self._specs.values()):
                if not self._check(version=release.version, spec=spec):
                    break
            else:
                result.add(release)
        return result

    def __str__(self):
        specs = sorted(set(self._specs.values()))
        return ','.join(specs)

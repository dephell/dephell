from packaging.version import LegacyVersion, parse
from packaging.specifiers import InvalidSpecifier

from .specifier import Specifier
from .git_specifier import GitSpecifier


class RangeSpecifier:
    def __init__(self, spec=None):
        if spec is not None:
            self._specs = self._parse(spec)

    @staticmethod
    def _parse(spec) -> set:
        if not isinstance(spec, (list, tuple)):
            spec = str(spec).split(',')
        result = set()
        for constr in spec:
            constr = constr.strip()
            if constr in ('', '*'):
                continue
            constr = constr.replace('.x', '.*')
            constr = constr.replace('.X', '.*')

            # https://docs.npmjs.com/misc/semver#advanced-range-syntax

            if ' - ' in constr:
                if '.*' in constr:
                    raise InvalidSpecifier('cannot mix ranges and starred notation')
                left, right = constr.split(' - ', maxsplit=1)
                result.add(Specifier('>=' + left))
                result.add(Specifier('<=' + right))
                continue

            if constr[0] in '~^':
                version = parse(constr.lstrip('~^=').replace('.*', '.0'))
                if isinstance(version, LegacyVersion):
                    raise InvalidSpecifier(constr)
                parts = version.release + (0, 0)
                parts = tuple(map(str, parts))
                left = '.'.join(parts[:3])
                if constr[0] == '^':    # ^1.2.3 := >=1.2.3 <2.0.0
                    right = '.'.join([parts[0], '*'])
                elif constr[0] == '~':  # ~1.2.3 := >=1.2.3 <1.3.0
                    right = '.'.join([parts[0], parts[1], '*'])
                result.add(Specifier('>=' + left))
                result.add(Specifier('==' + right))
                continue

            result.add(Specifier(constr))
        return result

    def attach_time(self, releases) -> bool:
        """Attach time to all specifiers if possible
        """
        ok = False
        for spec in self._specs:
            if spec.time is None:
                attached = spec.attach_time(releases)
                if attached:
                    ok = True
        return ok

    def __add__(self, other):
        new = self.__class__()
        new._specs = self._specs.copy()
        attached = new._attach(other)
        if attached:
            return new
        return NotImplemented

    def __radd__(self, other):
        new = self.__class__()
        new._specs = self._specs.copy()
        attached = new._attach(other)
        if attached:
            return new
        return NotImplemented

    def __iadd__(self, other):
        attached = self._attach(other)
        if attached:
            return self
        return NotImplemented

    def _attach(self, other):
        if isinstance(other, GitSpecifier):
            self._specs.add(other)
            return True
        if isinstance(other, self.__class__):
            self._specs.update(other._specs)
            return True
        return False

    def __contains__(self, release):
        for specifier in self._specs:
            if release not in specifier:
                return False
        return True

    def __str__(self):
        return ','.join(sorted(map(str, self._specs)))

    def __repr__(self):
        return '{name}({spec})'.format(
            name=self.__class__.__name__,
            spec=str(self),
        )

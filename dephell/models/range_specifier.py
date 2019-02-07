# external
from packaging.specifiers import InvalidSpecifier
from packaging.version import LegacyVersion, parse

# app
from ..constants import JoinTypes, PYTHONS
from .git_specifier import GitSpecifier
from .specifier import Specifier


class RangeSpecifier:

    def __init__(self, spec=None):
        if spec is not None:
            subspecs = str(spec).split('||')
            if len(subspecs) > 1:
                self._specs = {type(self)(subspec) for subspec in subspecs}
                self.join_type = JoinTypes.OR
            else:
                self._specs = self._parse(spec)
                self.join_type = JoinTypes.AND

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

    def to_marker(self, name: str) -> str:
        sep = ' and ' if self.join_type == JoinTypes.AND else ' or '
        return '(' + sep.join([spec.to_marker(name) for spec in self._specs]) + ')'

    @property
    def python_compat(self) -> bool:
        for version in PYTHONS:
            if version in self:
                return True
        return False

    def __add__(self, other):
        new = type(self)()
        new._specs = self._specs.copy()
        attached = new._attach(other)
        if attached:
            return new
        return NotImplemented

    def __radd__(self, other):
        new = type(self)()
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
        if isinstance(other, type(self)):
            self._specs.update(other._specs)
            return True
        return False

    def __contains__(self, release) -> bool:
        rule = all if self.join_type == JoinTypes.AND else any
        return rule((release in specifier) for specifier in self._specs)

    def __str__(self):
        sep = ',' if self.join_type == JoinTypes.AND else ' || '
        return sep.join(sorted(map(str, self._specs)))

    def __repr__(self):
        return '{name}({spec})'.format(
            name=self.__class__.__name__,
            spec=str(self),
        )

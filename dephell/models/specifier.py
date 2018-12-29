# built-in
import operator

# external
from cached_property import cached_property
from packaging import specifiers
from packaging.version import LegacyVersion, parse

# app
from .release import Release


OPERATORS = {
    '==': operator.eq,
    '!=': operator.ne,

    '<=': operator.le,
    '>=': operator.ge,

    '<': operator.lt,
    '>': operator.gt,
}

OPERATORS_MERGE = {
    # different
    frozenset({'>', '<'}):      None,
    frozenset({'>=', '<='}):    '==',

    # equal
    frozenset({'>', '=='}):     None,
    frozenset({'<', '=='}):     None,
    frozenset({'==', '=='}):    '==',
    frozenset({'>=', '=='}):    '==',
    frozenset({'<=', '=='}):    '==',

    # greater than
    frozenset({'>=', '>='}):    '>=',
    frozenset({'>=', '>'}):     '>',
    frozenset({'>', '>'}):      '>',

    # less than
    frozenset({'<=', '<='}):    '<=',
    frozenset({'<=', '<'}):     '<',
    frozenset({'<', '<'}):      '<',
}


class Specifier:
    time = None

    def __init__(self, constr):
        self._spec = None
        try:
            self._spec = self._legacy = specifiers.LegacySpecifier(str(constr))
        except specifiers.InvalidSpecifier:
            self._legacy = None
        try:
            self._spec = self._semver = specifiers.Specifier(str(constr))
        except specifiers.InvalidSpecifier:
            self._semver = None
        if self._spec is None:
            raise specifiers.InvalidSpecifier(constr)

    def attach_time(self, releases) -> bool:
        for release in releases:
            if release.time.year != 1970:
                if str(release.version) == self._spec.version:
                    self.time = release.time
                    return True
        return False

    def _check_version(self, version):
        """
        https://www.python.org/dev/peps/pep-0440/
        """
        if isinstance(version, str):
            version = parse(version)

        # if both semver
        if self._semver is not None:
            if not isinstance(version, LegacyVersion):
                return version in self._semver

        # otherwise compare both as legacy
        if self._legacy is not None:
            version = LegacyVersion(str(version))
            return version in self._legacy

        # lovely case, isn't it?
        return False

    @property
    def operator(self):
        return OPERATORS.get(self._spec.operator)

    @cached_property
    def version(self):
        return parse(self._spec.version)

    # magic methods

    def __contains__(self, release):
        # compare version
        if not isinstance(release, Release):
            return self._check_version(version=release)

        # compare release by time
        if self.time is not None and release.time is not None:
            if '*' not in str(self._spec.version):
                operator = self.operator
                if operator is not None:
                    return operator(release.time, self.time)

        # compare release by version
        return self._check_version(version=release.version)

    def __str__(self):
        return str(self._spec)

    def __repr__(self):
        return '{name}({spec})'.format(
            name=self.__class__.__name__,
            spec=str(self._spec),
        )

    def __add__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        self_operator = self._spec.operator
        other_operator = other._spec.operator
        operators = frozenset({self_operator, other_operator})

        # both versions are equal
        if self.version == other.version:
            operator = OPERATORS_MERGE[operators]
            if operator is None:
                return NotImplemented
            return type(self)(operator + str(self.version))

        # empty interval or closed interval
        if self_operator in {'>', '>='} and other_operator in {'<', '<='}:
            return NotImplemented
        if other_operator in {'>', '>='} and self_operator in {'<', '<='}:
            return NotImplemented

        if self.version <= other.version:
            left, right = self, other
        else:
            left, right = other, self
        if '>' in left._spec.operator:
            if '==' in right._spec.operator:
                return right
            return left
        if '<' in right._spec.operator:
            if '==' in left._spec.operator:
                return left
            return right

        return NotImplemented

import operator

# external
from packaging import specifiers
from packaging.version import LegacyVersion, parse

from .release import Release


class CompareTime:
    """
    In packaging.Specifier in every compare method hardcoded self._coerce_version.
    So we have to make our own methods without this junk.
    """
    equal = staticmethod(operator.eq)
    not_equal = staticmethod(operator.ne)

    less_than_equal = staticmethod(operator.le)
    greater_than_equal = staticmethod(operator.ge)

    less_than = staticmethod(operator.lt)
    greater_than = staticmethod(operator.gt)


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
        name = self._spec._operators[self._spec.operator]
        return getattr(CompareTime, name)

    # magic methods

    def __contains__(self, release):
        # compare version
        if not isinstance(release, Release):
            return self._check_version(version=release)
        # compare release by time
        if self.time is not None and release.time is not None:
            return self.operator(release.time, self.time)
        # compare release by version
        return self._check_version(version=release.version)

    def __str__(self):
        return str(self._spec)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, str(self._spec))

# external
from packaging import specifiers
from packaging.version import LegacyVersion, parse

from .release import Release


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
            if str(release.version) == self._spec.version:
                self.time = release.time
                return True
        return False

    def _check_version(self, version):
        if isinstance(version, str):
            version = parse(version)

        # if both semver
        if not isinstance(version, LegacyVersion):
            return version in self._semver

        # otherwise compare both as legacy
        version = LegacyVersion(str(version))
        return version in self._legacy

    @property
    def operator(self):
        return self._spec._get_operator(self._spec.operator)

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

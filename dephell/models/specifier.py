# external
from packaging import specifiers
from packaging.version import LegacyVersion


class Specifier:
    time = None

    def __init__(self, constr):
        self._legacy = specifiers.LegacySpecifier(str(constr))
        try:
            self._semver = specifiers.Specifier(str(constr))
        except specifiers.InvalidSpecifier:
            self._semver = None

    def attach_time(self, releases) -> bool:
        for release in releases:
            if str(release.version) == self._legacy.version:
                self.time = release.time
                return True
        return False

    def _check_version(self, version):
        # if both semver
        if not isinstance(version, LegacyVersion):
            return version in self._semver

        # otherwise compare both as legacy
        version = LegacyVersion(str(version))
        return version in self._legacy

    @property
    def operator(self):
        return self._legacy._get_operator(self._legacy.operator)

    def __contains__(self, release):
        if self.time is not None and release.time is not None:
            return self.operator(release.time, self.time)
        return self._check_version(version=release.version)

    def __str__(self):
        return str(self._legacy)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, str(self._legacy))

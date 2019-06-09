# built-in
from datetime import datetime
from typing import Optional

# app
from ..models.release import Release
from .base import Interface


class ReleaseRepo(Interface):
    """Repository with one dummy release
    """
    def __init__(self, *releases, link=None, deps=None):
        self._link = link
        self.releases = tuple(releases)
        self.deps = deps

    def get_releases(self, dep) -> tuple:
        if self.releases:
            return tuple(release for release in self.releases if release.name == dep.base_name)

        release = Release(
            raw_name=dep.raw_name,
            version='1.0',
            time=datetime(1970, 1, 1, 0, 0),
            hashes=getattr(self._link, 'hashes', ()),
        )
        return (release, )

    async def get_dependencies(self, name: str, version: str, extra: Optional[str] = None) -> tuple:
        if self.deps is None:
            return ()
        if extra is not None:
            name += '[' + extra + ']'
        return self.deps.get(name, {}).get(str(version), ())

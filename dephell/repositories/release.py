from ..models.release import Release
from datetime import datetime
from .base import Interface


class ReleaseRepo(Interface):
    """Repository with one dummy release
    """
    def __init__(self, link, release=None):
        self._link = link
        self.release = release

    def get_releases(self, dep) -> tuple:
        if self.release:
            return (self.release,)

        release = Release(
            raw_name=dep.name,
            version='1.0',
            time=datetime(1970, 1, 1, 0, 0),
            hashes=getattr(self._link, 'hashes', ()),
        )
        return (release, )

    async def get_dependencies(self, name: str, version: str) -> tuple:
        return ()

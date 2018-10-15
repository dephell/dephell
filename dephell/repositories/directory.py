from ..models.release import Release
from datetime import datetime
from .base import Interface
from .parsers import get_hash_from_link, get_name_from_link
from cached_property import cached_property


class DirectoryRepo(Interface):
    def __init__(self, path, name=None, digest=None):
        self._path = path
        if name:
            self.name = name
        if digest:
            self.hash = digest

    # properties

    @cached_property
    def name(self):
        return get_name_from_link(self._path)

    @cached_property
    def hash(self):
        digest = get_hash_from_link(self._path)
        # TODO: get dir hash
        return digest

    @property
    def link(self):
        return self.path

    # methods

    def get_releases(self, dep) -> tuple:
        release = Release(
            raw_name=dep.name,
            version='1.0',
            time=datetime(1970, 1, 1, 0, 0),
            hashes=(self.hash,) if self.hash else (),
        )
        return (release, )

    async def get_dependencies(self, name: str, version: str) -> tuple:
        # TODO: read package dependencies via converters
        return ()

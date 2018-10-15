from pathlib import Path
from hashlib import sha256
from ..models.release import Release
from datetime import datetime
from .base import Interface
from .parsers import get_hash_from_link, get_name_from_link
from cached_property import cached_property


class FileRepo(Interface):
    def __init__(self, path):
        self._path = path

    # properties

    @cached_property
    def name(self):
        return get_name_from_link(self._path)

    @cached_property
    def hash(self):
        digest = get_hash_from_link(self._path)
        if digest:
            return digest

        path = Path(self._path)
        if not path.is_file():
            return

        with path.open('rb') as stream:
            content = stream.read()
        hasher = sha256()
        hasher.update(content)
        return 'sha256:' + hasher.digest()

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
        return ()

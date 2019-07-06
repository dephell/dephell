# built-in
import re
from datetime import datetime
from hashlib import sha256
from logging import getLogger
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# external
import attr
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

# app
from ...cache import TextCache
from ...config import config
from ...constants import ARCHIVE_EXTENSIONS
from ...models.release import Release
from ._base import WarehouseBaseRepo


logger = getLogger('dephell.repositories.warehouse.simple')
REX_WORD = re.compile('[a-zA-Z]+')


@attr.s()
class WarehouseLocalRepo(WarehouseBaseRepo):
    name = attr.ib(type=str)
    path = attr.ib(type=Path)

    prereleases = attr.ib(type=bool, factory=lambda: config['prereleases'])  # allow prereleases
    from_config = attr.ib(type=bool, default=False)
    propagate = True  # deps of deps will inherit repo

    def __attrs_post_init__(self):
        if isinstance(self.path, str):
            self.path = Path(self.path)

    def get_releases(self, dep) -> tuple:

        releases_info = dict()
        for archive_path in self.path.glob('**/*'):
            if not archive_path.name.endswith(ARCHIVE_EXTENSIONS):
                continue
            name, version = self._parse_name(archive_path.name)
            if canonicalize_name(name) != dep.name:
                continue
            if not version:
                continue

            if version not in releases_info:
                releases_info[version] = []
            releases_info[version].append(self._get_hash(path=archive_path))

        # init releases
        releases = []
        prereleases = []
        for version, hashes in releases_info.items():
            # ignore version if no files for release
            release = Release(
                raw_name=dep.raw_name,
                version=version,
                time=datetime.fromtimestamp(self.path.stat().st_mtime),
                hashes=hashes,
                extra=dep.extra,
            )

            # filter prereleases if needed
            if release.version.is_prerelease:
                prereleases.append(release)
                if not self.prereleases and not dep.prereleases:
                    continue

            releases.append(release)

        # special case for black: if there is no releases, but found some
        # prereleases, implicitly allow prereleases for this package
        if not releases and prereleases:
            releases = prereleases

        releases.sort(reverse=True)
        return tuple(releases)

    async def get_dependencies(self, name: str, version: str,
                               extra: Optional[str] = None) -> Tuple[Requirement, ...]:
        cache = TextCache('warehouse-local', 'deps', name, str(version))
        deps = cache.load()
        if deps is None:
            deps = self._get_deps_from_files(name=name, version=version)
            cache.dump(deps)
        elif deps == ['']:
            return ()
        return self._convert_deps(deps=deps, name=name, version=version, extra=extra)

    def search(self, query: Iterable[str]) -> List[Dict[str, str]]:
        raise NotImplementedError

    @staticmethod
    def _get_hash(path: Path) -> str:
        digest = sha256()
        with path.open('rb') as stream:
            for byte_block in iter(lambda: stream.read(4096), b''):
                digest.update(byte_block)
        return digest.hexdigest()

    def _get_deps_from_files(self, name, version):
        from ...converters import SDistConverter, WheelConverter

        paths = []
        for path in self.path.glob('**/*'):
            if not path.name.endswith(ARCHIVE_EXTENSIONS):
                continue
            file_name, file_version = self._parse_name(path.name)
            if canonicalize_name(file_name) != name:
                continue
            if not file_version or file_version != str(version):
                continue
            paths.append(path)

        sdist = SDistConverter()
        wheel = WheelConverter()
        rules = (
            (wheel, 'py3-none-any.whl'),
            (wheel, '-none-any.whl'),
            (wheel, '.whl'),
            (sdist, '.tar.gz'),
            (sdist, '.zip'),
        )

        for converter, ext in rules:
            for path in paths:
                if not path.name.endswith(ext):
                    continue
                root = converter.load(path)
                deps = []
                for dep in root.dependencies:
                    if dep.envs == {'main'}:
                        deps.append(str(dep))
                    else:
                        for env in dep.envs.copy() - {'main'}:
                            dep.envs = {env}
                            deps.append(str(dep))
                return tuple(deps)
        return ()

# built-in
from base64 import urlsafe_b64encode
from hashlib import sha256
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

# external
from dephell_archive import ArchivePath
from dephell_discover import Root as PackageRoot

# app
from ..models import RootDependency
from .base import BaseConverter
from .egginfo import EggInfoConverter


class _Reader:

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if content is not None:
            return False
        # metadata file or dir for dists
        if path.name in ('dist', 'METADATA'):
            return True
        # extracted wheel
        if path.is_dir():
            return (path / 'METADATA').exists()
        # archived wheel
        return (path.suffix in ('.whl', '.zip'))

    def load(self, path) -> RootDependency:
        """Parse wheel

        Supported path format:
            + *.whl archive,
            + extracted *.whl (*.dist-info)
            + METADATA file from *.whl
        """
        path = Path(str(path))
        paths = None

        # if passed METADATA, just parse and return it
        if path.is_file() and path.suffix not in ('.whl', '.zip'):
            return self.loads(content=path.read_text())

        with TemporaryDirectory() as cache:
            if path.is_file() and path.suffix in ('.whl', '.zip'):
                path = ArchivePath(archive_path=path, cache_path=Path(cache))

            if not (path / 'METADATA').exists():
                paths = list(path.glob('*.dist-info/METADATA'))
                if not paths:
                    raise FileNotFoundError('cannot find METADATA in dir', str(path))
                # maybe it's possible, so we will have to process it
                if len(paths) > 1:
                    raise FileExistsError('too many METADATA in dir')
                path = paths[0].parent

            return self.load_dir(path)

    def load_dir(self, path) -> RootDependency:
        if not (path / 'METADATA').exists():
            raise FileNotFoundError('cannot find METADATA: {}'.format(str(path)))
        converter = EggInfoConverter()

        # dependency_links.txt
        urls = dict()
        if (path / 'dependency_links.txt').exists():
            with (path / 'dependency_links.txt').open('r') as stream:
                content = stream.read()
            urls = converter.parse_dependency_links(content)

        # METADATA
        with (path / 'METADATA').open('r') as stream:
            content = stream.read()
        root = converter.parse_info(content, urls=urls)

        # entry_points.txt
        if (path / 'entry_points.txt').exists():
            with (path / 'entry_points.txt').open('r') as stream:
                content = stream.read()
            root = converter.parse_entrypoints(content, root=root)

        root.package = PackageRoot(path=path.parent, name=root.name)
        return root

    def loads(self, content: str) -> RootDependency:
        """Parse METADATA file from .whl archive
        """
        # "METADATA is the package metadata, the same format as PKG-INFO"
        # (c) PEP-0427
        return EggInfoConverter().parse_info(content)


class _Writer:
    def dump(self, reqs, path: Path, project: RootDependency) -> None:
        path = self._get_path(path=path, project=project)
        path.parent.mkdir(exist_ok=True, parents=True)
        if path.exists():
            path.unlink()

        converter = EggInfoConverter()
        getters = {
            'dependency_links.txt': lambda: converter.make_dependency_links(reqs=reqs),
            'entry_points.txt': lambda: converter.make_entrypoints(project=project),
            'METADATA': lambda: converter.make_info(reqs=reqs, project=project, with_requires=True),
            'top_level.txt': lambda: converter.make_top_level(project=project),
            'WHEEL': lambda: self.make_wheel(project=project),
        }

        self._records = []
        base_path = '{}-{}.dist-info/'.format(project.name, str(project.version))
        with path.open('w+b') as stream:
            with ZipFile(stream, mode='w', compression=ZIP_DEFLATED) as archive:
                # write metafiles
                for fname, getter in getters.items():
                    self._write_content(archive=archive, path=base_path + fname, content=getter())

                # write packages
                for package in chain(project.package.packages, project.package.data):
                    for full_path in package:
                        self._write_file(
                            archive=archive,
                            path='/'.join(full_path.relative_to(project.package.path).parts),
                            fpath=full_path,
                        )

                # write license files
                patterns = ('LICEN[CS]E*', 'COPYING*', 'NOTICE*', 'AUTHORS*')
                for pattern in patterns:
                    for file_path in project.package.path.glob(pattern):
                        if not file_path.is_file():
                            continue
                        self._write_file(
                            archive=archive,
                            path=base_path + file_path.name,
                            fpath=file_path,
                        )

                # write RECORD
                self._write_content(
                    archive=archive,
                    path=base_path + 'RECORD',
                    content=self.make_records(path=base_path + 'RECORD'),
                )

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        return EggInfoConverter().dumps(reqs=reqs, project=project, content=content)

    @staticmethod
    def _get_path(path, project):
        if isinstance(path, str):
            path = Path(path)
        if path.suffix not in ('.whl', '.zip'):
            path /= '{name}-{version}-py3-none-any.whl'.format(
                name=project.name.replace('-', '_'),
                version=str(project.version),
            )
        return path

    def _write_content(self, archive, path: str, content: str) -> None:
        content = content.encode('utf-8')

        # write content into archive
        zip_info = ZipInfo(path)
        archive.writestr(zip_info, content, compress_type=ZIP_DEFLATED)

        # calculate hashsum
        digest = sha256(content).digest()
        digest = urlsafe_b64encode(digest).decode().rstrip('=')
        self._records.append((path, digest, len(content)))

    def _write_file(self, archive, path: str, fpath: Path) -> None:
        # write content into archive
        archive.write(filename=str(fpath), arcname=path, compress_type=ZIP_DEFLATED)

        # calculate hashsum
        # https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
        digest = sha256()
        with fpath.open('rb') as stream:
            while True:
                data = stream.read(65536)
                if not data:
                    break
                digest.update(data)
        digest = urlsafe_b64encode(digest.digest()).decode().rstrip('=')

        self._records.append((path, digest, fpath.stat().st_size))

    @staticmethod
    def make_wheel(project: RootDependency) -> str:
        return (
            'Wheel-Version: 1.0\n'
            'Generator: dephell (0.1.0)\n'
            'Root-Is-Purelib: true\n'
            'Tag: py3-none-any\n'
        )

    def make_records(self, path: str) -> str:
        content = '\n'.join('{},sha256={},{}'.format(*record) for record in self._records)
        return content + ('\n{},,'.format(path))


class WheelConverter(_Reader, _Writer, BaseConverter):
    """
    PEP-0427
    https://www.python.org/dev/peps/pep-0427/
    """
    lock = False

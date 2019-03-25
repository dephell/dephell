# built-in
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

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

        # METADATA
        with (path / 'METADATA').open('r') as stream:
            content = stream.read()
        root = converter.parse_info(content)

        # entry_points.txt
        if (path / 'entry_points.txt').exists():
            with (path / 'entry_points.txt').open('r') as stream:
                content = stream.read()
            root = converter.parse_entrypoints(content, root=root)

        root.package = PackageRoot(path=path.parent)
        return root

    def loads(self, content: str) -> RootDependency:
        """Parse METADATA file from .whl archive
        """
        # "METADATA is the package metadata, the same format as PKG-INFO"
        # (c) PEP-0427
        return EggInfoConverter().parse_info(content)


class _Writer:

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        return EggInfoConverter().dumps(reqs=reqs, project=project, content=content)

    @staticmethod
    def make_wheel(paroject: RootDependency) -> str:
        return (
            'Wheel-Version: 1.0\n'
            'Generator: dephell (0.1.0)\n'
            'Root-Is-Purelib: true\n'
            'Tag: py3-none-any\n',
        )


class WheelConverter(_Reader, _Writer, BaseConverter):
    """
    PEP-0427
    https://www.python.org/dev/peps/pep-0427/
    """
    lock = False

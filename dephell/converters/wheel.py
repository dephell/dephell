# built-in
from pathlib import Path
from tempfile import TemporaryDirectory

# project
from dephell_archive import ArchivePath

# app
from ..models import RootDependency
from .base import BaseConverter
from .egginfo import EggInfoConverter


class WheelConverter(BaseConverter):
    """
    PEP-0427
    https://www.python.org/dev/peps/pep-0427/
    """
    lock = False

    def load(self, path) -> RootDependency:
        """Parse wheel

        Supported path format:
            + *.whl archive,
            + extracted *.whl (*.dist-info)
            + METADATA file from *.whl
        """
        path = Path(str(path))
        paths = None

        with TemporaryDirectory() as cache:
            # passed .whl archive
            if path.is_file() and path.suffix == '.whl':
                archive = ArchivePath(archive_path=path, cache_path=Path(cache))
                paths = list(archive.glob('*.dist-info/METADATA'))

            # passed extracted .whl
            if path.is_dir():
                paths = [path / 'METADATA']
                if not path.exists():
                    paths = list(path.glob('*.dist-info/METADATA'))

            # passed METADATA file
            if paths is None:
                paths = [path]

            if not paths:
                raise FileNotFoundError('cannot find METADATA in dir', str(path))
            # maybe it's possible, so we will have to process it
            if len(paths) > 1:
                raise FileExistsError('too many METADATA in dir')

            with paths[0].open('r') as stream:
                content = stream.read()

        return self.loads(content)

    def loads(self, content: str) -> RootDependency:
        """Parse METADATA file from .whl archive
        """
        # "METADATA is the package metadata, the same format as PKG-INFO"
        # (c) PEP-0427
        return EggInfoConverter()._parse_info(content)

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        return EggInfoConverter().dumps(reqs=reqs, project=project, content=content)

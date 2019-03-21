# built-in
from pathlib import Path
from tempfile import TemporaryDirectory

# project
from dephell_archive import ArchivePath

# app
from ..controllers import Readme
from ..models import RootDependency
from .base import BaseConverter
from .egginfo import EggInfoConverter


class SDistConverter(BaseConverter):
    lock = False

    def load(self, path) -> RootDependency:
        path = Path(str(path))
        if path.suffix not in ('.zip', '.gz', '.tar'):
            raise ValueError('invalid file extension: ' + path.suffix)

        with TemporaryDirectory() as cache:
            archive = ArchivePath(archive_path=path, cache_path=Path(cache))
            paths = list(archive.glob('**/*.egg-info'))
            root = EggInfoConverter().load_dir(*paths)
            root.readme = Readme.discover(path=archive)
            return root

    def dump(self, reqs, path, project: RootDependency) -> None:
        ...

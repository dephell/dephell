# built-in
from email.parser import Parser
from pathlib import Path

# external
from packaging.requirements import Requirement

# app
from ..archive import ArchivePath
from ..models import Dependency, RootDependency
from .base import BaseConverter


class WheelConverter(BaseConverter):
    def load(self, path) -> RootDependency:
        """Parse wheel

        Supported path format:
            + *.whl archive,
            + extracted *.whl (*.dist-info)
            + METADATA file from *.whl
        """
        path = Path(str(path))
        paths = None

        # passed .whl archive
        if path.is_file() and path.suffix == '.whl':
            archive = ArchivePath(path)
            paths = list(archive.glob('**/METADATA'))

        # passed extracted .whl
        if path.is_dir():
            paths = [path / 'METADATA']
            if not path.exists():
                paths = list(path.glob('**/*.dist-info/METADATA'))

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
        info = Parser().parsestr(content)
        root = RootDependency(name=info.get('Name').strip())
        deps = []
        for req in info.get_all('Requires-Dist'):
            req = Requirement(req)
            deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

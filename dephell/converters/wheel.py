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
        path = Path(str(path))
        if path.suffix == '.whl':
            # new_path = extract(path=path, patterns=['*METADATA'])
            ...

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

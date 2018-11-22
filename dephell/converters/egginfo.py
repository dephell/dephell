from email.parser import Parser
from pathlib import Path

from packaging.requirements import Requirement

from .base import BaseConverter
from ..models import Dependency, RootDependency


class EggInfoConverter(BaseConverter):
    lock = False

    def load(self, path) -> RootDependency:
        path = Path(str(path))
        with (path / 'PKG-INFO').open('r') as stream:
            info = Parser().parse(stream)
        root = RootDependency(name=info.get('Name').strip())

        deps = []
        with (path / 'requires.txt').open('r') as stream:
            for req in stream:
                req = Requirement(req)
                deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

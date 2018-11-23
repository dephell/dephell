# built-in
from email.parser import Parser
from pathlib import Path

# external
from packaging.requirements import Requirement as PackagingRequirement

# app
from ..models import Dependency, RootDependency
from .base import BaseConverter


class EggInfoConverter(BaseConverter):
    """
    PEP-314
    """
    lock = False

    def load(self, path) -> RootDependency:
        path = Path(str(path))
        if path.is_dir():
            with (path / 'PKG-INFO').open('r') as stream:
                root = self._parse_info(stream.read())
            path = path / 'requires.txt'
            if not root.dependencies and path.exists():
                with path.open('r') as stream:
                    root = self._parse_requires(stream.read(), root=root)
            return root

        with path.open('r') as stream:
            return self.loads(stream.read())

    def loads(self, content: str) -> RootDependency:
        if 'Requires: ' in content:
            return self._parse_info(content)
        else:
            return self._parse_requires(content)

    def dumps(self, reqs, content=None) -> str:
        content = []
        ...
        return '\n'.join(content)

    # helpers

    def _parse_info(self, content: str, root=None) -> RootDependency:
        info = Parser().parsestr(content)
        root = RootDependency(name=info.get('Name').strip())
        deps = []
        for req in info.get_all('Requires'):
            req = PackagingRequirement(req)
            deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

    def _parse_requires(self, content: str, root=None) -> RootDependency:
        if root is None:
            root = RootDependency(name=self._get_name(content=content))
        deps = []
        for req in content.split:
            req = PackagingRequirement(req)
            deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

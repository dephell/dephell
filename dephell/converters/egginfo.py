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
        # distutils.dist.DistributionMetadata.write_pkg_file
        content = []
        content.append(('Metadata-Version', '1.1'))
        # TODO: get project info
        content.append(('Name', 'UNKNOWN'))
        content.append(('Version', '0.0.0'))

        for req in reqs:
            content.append(('Requires', self._format_req(req=req)))
        return '\n'.join(map(': '.join, content))

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

    def _format_req(self, req):
        line = req.name
        if req.extras:
            line += '[{extras}]'.format(extras=','.join(req.extras))
        if req.version:
            line += req.version
        if req.markers:
            line += '; ' + req.markers
        return line

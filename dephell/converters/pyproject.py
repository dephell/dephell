# built-in
from pathlib import Path
from typing import Optional

# external
from dephell_discover import Root as PackageRoot
from packaging.requirements import Requirement
from tomlkit import document, dumps, parse

# app
from ..controllers import DependencyMaker
from ..models import RootDependency
from .base import BaseConverter


class PyProjectConverter(BaseConverter):
    lock = False

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        if content:
            return '[build-system]' in content
        return path.name == 'pyproject.toml'

    def loads(self, content: str) -> RootDependency:
        doc = parse(content)
        deps = []
        root = RootDependency(
            package=PackageRoot(path=self.project_path or Path()),
        )
        for req in doc['build-system'].get('requires', []):
            req = Requirement(req)
            deps.extend(DependencyMaker.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        doc = document()
        deps = []
        for req in reqs:
            deps.append(self._format_req(req=req))
        doc['build-system']['requires'] = deps
        return dumps(doc)

    def _format_req(self, req):
        line = req.raw_name
        if req.extras:
            line += '[{extras}]'.format(extras=','.join(req.extras))
        line += req.version
        if req.markers:
            line += '; ' + req.markers
        return line

from tomlkit import parse, dumps, document
from packaging.requirements import Requirement

# app
from ..models import Dependency, RootDependency
from .base import BaseConverter


class PyProjectConverter(BaseConverter):
    lock = False

    def loads(self, content: str) -> RootDependency:
        doc = parse(content)
        deps = []
        root = RootDependency(name=self._get_name(content=content))
        for req in doc['build-system']['requires']:
            req = Requirement(req)
            deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, content=None) -> str:
        doc = document()
        deps = []
        for req in reqs:
            deps.append(self._format_req(req=req))
        doc['build-system']['requires'] = deps
        return dumps(doc)

    def _format_req(self, req):
        line = req.name
        if req.extras:
            line += '[{}]'.format(','.join(req.extras))
        line += req.version
        if req.markers:
            line += '; ' + req.markers
        return line

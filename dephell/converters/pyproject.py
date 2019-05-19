# external
from packaging.requirements import Requirement
from tomlkit import document, dumps, parse

# app
from ..controllers import DependencyMaker
from ..models import RootDependency
from .base import BaseConverter


class PyProjectConverter(BaseConverter):
    lock = False

    def loads(self, content: str) -> RootDependency:
        doc = parse(content)
        deps = []
        root = RootDependency()
        for req in doc['build-system']['requires']:
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

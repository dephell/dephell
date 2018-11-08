from pip._internal.download import PipSession
from pip._internal.req import parse_requirements
from ..models import Dependency, RootDependency
from .base import BaseConverter


class PIPConverter(BaseConverter):
    sep = ' \\\n  '

    def __init__(self, lock):
        self.lock = lock

    def load(self, path) -> RootDependency:
        deps = []
        root = RootDependency(name=self._get_name(path=path))
        # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/constructors.py
        for req in parse_requirements(str(path), session=PipSession()):
            # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/req_install.py
            deps.append(Dependency.from_requirement(root, req.req, url=req.link and req.link.url))
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs) -> str:
        deps = []
        for req in reqs:
            deps.append(self._format_req(req=req))
        deps.sort()
        return '\n'.join(deps) + '\n'

    # https://github.com/pypa/packaging/blob/master/packaging/requirements.py
    # https://github.com/jazzband/pip-tools/blob/master/piptools/utils.py
    def _format_req(self, req):
        line = req.name
        if req.extras:
            line += '[{}]'.format(','.join(req.extras))
        line += req.version
        if req.markers:
            line += '; ' + req.markers
        if req.hashes:
            for digest in req.hashes:
                # https://github.com/jazzband/pip-tools/blob/master/piptools/writer.py
                line += '{}--hash sha256:{}'.format(self.sep, digest)
        if req.sources:
            line += '{}# ^ from {}'.format(self.sep, ', '.join(req.sources))
        return line

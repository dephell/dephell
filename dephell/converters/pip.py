from pip._internal.download import PipSession
from pip._internal.req import parse_requirements
from ..models import Dependency, RootDependency


class PIPConverter:
    sep = ' \\\n  '

    def __init__(self, lock):
        self.lock = lock

    def loads(self, path) -> RootDependency:
        deps = []
        root = RootDependency()
        # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/constructors.py
        for req in parse_requirements(str(path), session=PipSession()):
            # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/req_install.py
            deps.append(Dependency.from_requirement(root, req.req, url=req.link and req.link.url))
        root.attach_dependencies(deps)
        return root

    def dumps(self, graph) -> str:
        deps = []
        for dep in graph.mapping.values():
            if not dep.used:
                continue
            deps.append(self._format_dep(dep))
        deps.sort()
        return '\n'.join(deps) + '\n'

    # https://github.com/pypa/packaging/blob/master/packaging/requirements.py
    # https://github.com/jazzband/pip-tools/blob/master/piptools/utils.py
    def _format_dep(self, dep):
        if self.lock:
            release = dep.group.best_release
        line = dep.name
        if dep.extras:
            line += '[{}]'.format(','.join(sorted(dep.extras)))
        if self.lock:
            line += '==' + str(release.version)
        else:
            line += str(dep.constraint)
        if dep.marker:
            line += '; ' + str(dep.marker)
        if self.lock:
            for digest in release.hashes:
                # https://github.com/jazzband/pip-tools/blob/master/piptools/writer.py
                line += '{}--hash sha256:{}'.format(self.sep, digest)
        if not dep.constraint.empty:
            line += '{}# ^ from {}'.format(self.sep, ', '.join(dep.constraint.sources))
        return line

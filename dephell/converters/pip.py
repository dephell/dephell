from pip._internal.download import PipSession
from pip._internal.req import parse_requirements
from ..models import Dependency, RootDependency


def from_pip(path):
    deps = []
    root = RootDependency()
    # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/constructors.py
    for req in parse_requirements(str(path), session=PipSession()):
        # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/req_install.py
        deps.append(Dependency.from_requirement(root, req.req, url=req.link and req.link.url))
    root.attach_dependencies(deps)
    return root


def to_pip(graph):
    deps = []
    for dep in graph.mapping.values():
        if dep.used:
            deps.append(str(dep.group.best_release))
    deps.sort()
    return '\n'.join(deps) + '\n'

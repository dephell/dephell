from pip._internal.download import PipSession
from pip._internal.req import parse_requirements
from ..models import Dependency, RootDependency


SEP = ' \\\n  '


def from_pip(path) -> RootDependency:
    deps = []
    root = RootDependency()
    # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/constructors.py
    for req in parse_requirements(str(path), session=PipSession()):
        # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/req_install.py
        deps.append(Dependency.from_requirement(root, req.req, url=req.link and req.link.url))
    root.attach_dependencies(deps)
    return root


# https://github.com/pypa/packaging/blob/master/packaging/requirements.py
# https://github.com/jazzband/pip-tools/blob/master/piptools/utils.py
def _format_dep(dep, *, lock: bool):
    if lock:
        release = dep.group.best_release
    line = dep.name
    if dep.extras:
        line += '[{}]'.format(','.join(sorted(dep.extras)))
    if lock:
        line += '==' + str(release.version)
    else:
        line += str(dep.specifier)
    if dep.marker:
        line += '; ' + dep.marker
    if lock:
        for digest in release.hashes:
            # https://github.com/jazzband/pip-tools/blob/master/piptools/writer.py
            line += '{}--hash sha256:{}'.format(SEP, digest)
    if not dep.constraint.empty:
        line += '{}# ^ from {}'.format(SEP, ', '.join(dep.constraint.sources))
    return line


def to_pip(graph, *, lock: bool=False) -> str:
    deps = []
    for dep in graph.mapping.values():
        if not dep.used:
            continue
        deps.append(_format_dep(dep, lock=lock))
    deps.sort()
    return '\n'.join(deps) + '\n'

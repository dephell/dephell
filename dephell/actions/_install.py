# built-in
from pathlib import Path

# app
from ..controllers import Resolver, analyze_conflict
from ..models import Requirement
from ..package_manager import PackageManager
from ._package import get_resolver


def install_deps(resolver: Resolver, python_path: Path, silent: bool, logger=None) -> bool:
    # resolve
    if logger is not None:
        logger.info('build dependencies graph...')
    resolved = resolver.resolve(silent=silent)
    if not resolved:
        conflict = analyze_conflict(resolver=resolver)
        if logger is not None:
            logger.warning('conflict was found')
        print(conflict)
        return False

    # install
    reqs = Requirement.from_graph(graph=resolver.graph, lock=True)
    if logger is not None:
        logger.info('installation...', extra=dict(
            executable=python_path,
            packages=len(reqs),
        ))
    code = PackageManager(executable=python_path).install(reqs=reqs)
    if code != 0:
        return False
    if logger is not None:
        logger.info('installed')
    return True


def install_dep(name: str, python_path: Path, silent: bool, logger=None) -> bool:
    return install_deps(
        resolver=get_resolver(reqs=[name]),
        python_path=python_path,
        logger=logger,
        silent=silent,
    )

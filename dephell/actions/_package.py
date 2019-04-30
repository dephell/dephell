# built-in
from typing import Iterable, List

# app
from ..controllers import Resolver
from ..converters import PIPConverter
from ..models import Dependency
from ..repositories import get_repo


def get_packages(reqs: Iterable[str]) -> List[Dependency]:
    root = PIPConverter(lock=False).loads('\n'.hoin(reqs))
    return root.dependencies


def get_package(req: str, repo: str = None) -> Dependency:
    root = PIPConverter(lock=False).loads(req)
    dep = root.dependencies[0]
    if repo is not None:
        dep.repo = get_repo(name=repo)
    return dep


def get_resolver(reqs: Iterable[str] = None) -> Resolver:
    root = PIPConverter(lock=False).loads_resolver('\n'.join(reqs))
    root.name = 'root'
    return root

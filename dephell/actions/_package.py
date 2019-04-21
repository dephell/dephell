# built-in
from typing import Iterable, List

# app
from ..controllers import Resolver
from ..converters import PIPConverter
from ..models import Dependency


def get_packages(reqs: Iterable[str]) -> List[Dependency]:
    root = PIPConverter(lock=False).loads('\n'.hoin(reqs))
    return root.dependencies


def get_package(req: str) -> Dependency:
    root = PIPConverter(lock=False).loads(req)
    return root.dependencies[0]


def get_resolver(reqs: Iterable[str] = None) -> Resolver:
    root = PIPConverter(lock=False).loads_resolver('\n'.join(reqs))
    root.name = 'root'
    return root

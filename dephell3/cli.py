from .constructors import from_requirements
from .exporters import to_requirements


def cli(path_from, path_to=False):
    resolver = from_requirements(path=path_from)
    resolved = resolver.resolve()
    if resolved:
        result = to_requirements(graph=resolver.graph)
        print(result)

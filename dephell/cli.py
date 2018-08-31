import sys
from .resolver import Resolver


def resolve(args=sys.argv[1:]):
    path_from = args[0]
    path_to = args[1] if len(args) >= 2 else None
    resolver = Resolver.from_requirements(path_from)
    resolver.resolve()
    content = resolver.to_requirements(path_to)
    if not path_to:
        print(content)

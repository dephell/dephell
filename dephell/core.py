from pathlib import Path
from .controllers import Graph, Mutator, Resolver
from .converters import LOADERS, DUMPERS


def load(loader, path):
    loader = LOADERS[loader]
    root = loader(path)
    graph = Graph(root)
    return Resolver(
        graph=graph,
        mutator=Mutator()
    )


def dump(dumper, path, graph):
    dumper = DUMPERS[dumper]
    content = dumper(graph)
    if not isinstance(path, Path):
        path = Path(path)
    with path.open('w') as stream:
        stream.write(content)


def analize_conflict(graph):
    conflict = graph.conflict.name
    constraint = str(graph.conflict.constraint)
    return '{} {}'.format(conflict, constraint)

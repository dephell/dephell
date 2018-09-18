from pathlib import Path
from .controllers import Graph, Mutator, Resolver
from .converters import CONVERTERS


def load(loader, path):
    loader = CONVERTERS[loader]
    root = loader.loads(path)
    return Resolver(
        graph=Graph(root),
        mutator=Mutator()
    )


def dump(dumper, path, graph):
    dumper = CONVERTERS[dumper]
    content = dumper.dumps(graph)
    if not isinstance(path, Path):
        path = Path(path)
    with path.open('w') as stream:
        stream.write(content)


def analize_conflict(graph):
    conflict = graph.conflict.name
    constraint = str(graph.conflict.constraint)
    return '{} {}'.format(conflict, constraint)

# built-in
from unittest.mock import patch

# project
from dephell.controllers import Graph, Mutator, Resolver

# app
from ..helpers import Fake, make_root


def check(root, conflict, mutations):
    resolver = Resolver(
        graph=Graph(root),
        mutator=Mutator(),
    )
    with patch(
        target='dephell.controllers._dependency.get_repo',
        return_value=resolver.graph._roots[0].repo,
    ):
        resolver.resolve(debug=True)

    graph = resolver.graph
    graph.conflict = graph.get(conflict)
    assert graph.conflict is not None

    mutator = Mutator()
    for _ in range(10):
        groups = mutator.mutate(graph)
        # if cannot mutate
        if groups is None:
            break
        for group in groups:
            dep = graph.get(group.name)
            dep.group = group

    assert mutator.mutations == mutations


def test_mutator_diamond():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(
            Fake('1.0', 'c==1.0'),
            Fake('2.0', 'c==2.0'),
        ),
        b=(
            Fake('1.0', 'c==1.0'),
            Fake('2.0', 'c==2.0'),
        ),
        c=(
            Fake('1.0'),
            Fake('2.0'),
        ),
    )
    check(root=root, conflict='c', mutations=4)

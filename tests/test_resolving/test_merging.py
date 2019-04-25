# project
from dephell.controllers import Graph, Mutator, Resolver, analyze_conflict

# app
from ..helpers import Fake, make_root


def merge(*roots, merged=True, deps=None):
    graph = Graph()
    for root in roots:
        graph.add(root)
    resolver = Resolver(graph=graph, mutator=Mutator())
    resolved = resolver.resolve(level=1)

    try:
        assert merged == resolved
    except AssertionError:
        if resolved is False:
            print(analyze_conflict(resolver=resolver))
        raise

    if deps:
        for dep in deps:
            assert dep in resolver.graph
        names = set(resolver.graph.names) - set(root.name for root in roots)
        assert names == set(deps)

    return resolver


def test_simple_merge():
    root1 = make_root(
        root=Fake('', 'a', 'b'),
        a=(Fake('1.0'), ),
        b=(Fake('1.0'), ),
    )
    root2 = make_root(
        root=Fake('', 'c', 'd'),
        c=(Fake('1.0'), ),
        d=(Fake('1.0'), ),
    )
    merge(root1, root2, deps=('a', 'b', 'c', 'd'))


def test_merge_with_common_dep():
    root1 = make_root(
        root=Fake('', 'a', 'b'),
        a=(Fake('1.0'), ),
        b=(Fake('1.0'), ),
    )
    root2 = make_root(
        root=Fake('', 'b', 'c'),
        b=(Fake('1.0'), ),
        c=(Fake('1.0'), ),
    )
    merge(root1, root2, deps=('a', 'b', 'c'))


def test_merge_with_constraint():
    root1 = make_root(
        root=Fake('', 'a', 'b>=1.0'),
        a=(Fake('1.0'), ),
        b=(Fake('1.0'), Fake('2.0')),
    )
    root2 = make_root(
        root=Fake('', 'b<2.0', 'c'),
        b=(Fake('1.0'), Fake('2.0')),
        c=(Fake('1.0'), ),
    )
    resolver = merge(root1, root2, deps=('a', 'b', 'c'))
    constraint = str(resolver.graph.get('b').constraint)
    assert constraint == '<2.0,>=1.0'


def test_merge_conflict():
    root1 = make_root(
        root=Fake('', 'a', 'b<=1.0'),
        a=(Fake('1.0'), ),
        b=(Fake('1.0'), Fake('2.0')),
    )
    root2 = make_root(
        root=Fake('', 'b>=2.0', 'c'),
        b=(Fake('1.0'), Fake('2.0')),
        c=(Fake('1.0'), ),
    )
    resolver = merge(root1, root2, merged=False)
    assert resolver.graph.conflict.name == 'b'

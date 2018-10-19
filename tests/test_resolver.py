from .factories import make_root
from dephell.controllers import Graph, Mutator, Resolver
from unittest.mock import patch


def test_constraint_checks():
    root = make_root(
        root=dict(
            a='*',
            b='<1.1',
        ),
        releases=dict(
            a=('1.0', ),
            b=('1.0', '1.1'),
        ),
        constraints=dict(),
    )

    resolver = Resolver(
        graph=Graph(root),
        mutator=Mutator()
    )
    with patch(
        target='dephell.models.dependency.get_repo',
        return_value=resolver.graph.root.repo,
    ):
        resolved = resolver.resolve()
    assert resolved
    assert resolver.graph.get('root').applied
    reqs = resolver.graph.get_requirements(lock=True)
    reqs = {req.name: req for req in reqs}
    assert reqs['a'].version == '==1.0'
    assert reqs['b'].version == '==1.0'


def test_more_complex_constraint():
    root = make_root(
        root=dict(
            a='*',
            b='<=1.3,!=1.3,!=1.2',
        ),
        releases=dict(
            a=('1.0', ),
            b=('1.0', '1.1', '1.2', '1.3'),
        ),
        constraints=dict(),
    )

    resolver = Resolver(
        graph=Graph(root),
        mutator=Mutator()
    )
    with patch(
        target='dephell.models.dependency.get_repo',
        return_value=resolver.graph.root.repo,
    ):
        resolved = resolver.resolve()
    assert resolved
    assert resolver.graph.get('root').applied
    reqs = resolver.graph.get_requirements(lock=True)
    reqs = {req.name: req for req in reqs}
    assert reqs['a'].version == '==1.0'
    assert reqs['b'].version == '==1.1'


def test_all_have_constraints():
    root = make_root(
        root=dict(
            b='*',
        ),
        releases=dict(
            a=('1.0', ),
            b=('1.0', ),
            c=('1.0', ),
        ),
        constraints=dict(
            b={'1.0': ('a>=1.0', 'c>=1.0')},
            c={'1.0': 'a>=1.0'},
        ),
    )

    resolver = Resolver(
        graph=Graph(root),
        mutator=Mutator()
    )
    with patch(
        target='dephell.models.dependency.get_repo',
        return_value=resolver.graph.root.repo,
    ):
        resolved = resolver.resolve()
    assert resolved
    assert resolver.graph.get('root').applied
    reqs = resolver.graph.get_requirements(lock=True)
    reqs = {req.name: req for req in reqs}
    assert reqs['a'].version == '==1.0'
    assert reqs['b'].version == '==1.0'


def test_circular_dependency_on_older_version():
    root = make_root(
        root=dict(
            a='>=1.0.0',
        ),
        releases=dict(
            a=('1.0.0', '2.0.0'),
            b=('1.0.0', ),
        ),
        constraints=dict(
            a={'2.0.0': ('b==1.0.0')},
            b={'1.0.0': ('a==1.0.0')},
        ),
    )

    resolver = Resolver(
        graph=Graph(root),
        mutator=Mutator()
    )
    with patch(
        target='dephell.models.dependency.get_repo',
        return_value=resolver.graph.root.repo,
    ):
        resolved = resolver.resolve()
    assert resolved
    assert resolver.graph.get('root').applied
    reqs = resolver.graph.get_requirements(lock=True)
    reqs = {req.name: req for req in reqs}
    assert reqs['a'].version == '==1.0.0'
    assert 'b' not in reqs

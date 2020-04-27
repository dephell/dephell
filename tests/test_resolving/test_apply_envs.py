from dephell.controllers import Graph, Mutator, Resolver
from dephell.models import Requirement

# app
from ..helpers import Fake, check, make_root, set_envs


def fast_filter(root):
    resolver = Resolver(
        graph=Graph(root),
        mutator=Mutator(),
    )
    resolver.graph.fast_apply()
    resolver.apply_envs(envs={'main'})
    reqs = Requirement.from_graph(resolver.graph, lock=False)
    return {req.name: req for req in reqs}


def test_direct_dependencies():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(Fake('1.0'), ),
        b=(Fake('1.0'), ),
    )
    set_envs(root, 'a', {'main'})
    set_envs(root, 'b', {'dev'})
    check(root=root, a='==1.0', missed=['b'], envs={'main'})


def test_subdependencies():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(Fake('1.0'), ),
        b=(Fake('1.0', 'c'), ),
        c=(Fake('1.0'), ),
    )
    set_envs(root, 'a', {'main'})
    set_envs(root, 'b', {'dev'})
    check(root=root, a='==1.0', missed=['b', 'c'], envs={'main'})


def test_reapply():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(Fake('1.0', 'c'), ),
        b=(Fake('1.0', 'c'), ),
        c=(Fake('1.0'), ),
    )
    set_envs(root, 'a', {'main'})
    set_envs(root, 'b', {'dev'})
    check(root=root, a='==1.0', c='==1.0', missed=['b'], envs={'main'})


def test_unapply_twice():
    root = make_root(
        root=Fake('', 'a', 'b', 'c'),
        a=(Fake('1.0'), ),
        b=(Fake('1.0', 'd'), ),
        c=(Fake('1.0', 'd'), ),
        d=(Fake('1.0'), ),
    )
    set_envs(root, 'a', {'main'})
    set_envs(root, 'b', {'dev'})
    set_envs(root, 'c', {'dev'})
    check(root=root, a='==1.0', missed=['b', 'c', 'd'], envs={'main'})


def test_with_real_names():
    root = make_root(
        root=Fake('', 'bandit', 'boltons'),
        bandit=(Fake('1.0', 'colorama'), ),
        boltons=(Fake('1.0'), ),
        colorama=(Fake('1.0'), ),
    )
    set_envs(root, 'boltons', {'main'})
    set_envs(root, 'bandit', {'dev'})
    check(root=root, boltons='==1.0', missed=['bandit', 'colorama'], envs={'main'})


def test_deep_dependencies():
    root = make_root(
        root=Fake('', 'apiwrapper', 'sphinx', 'certifi'),
        sphinx=(Fake('1.0', 'requests'), ),
        apiwrapper=(Fake('1.0', 'requests'), ),
        requests=(Fake('1.0', 'certifi'), ),
        certifi=(Fake('1.0'), ),
    )
    set_envs(root, 'sphinx', {'main'})
    set_envs(root, 'apiwrapper', {'dev'})
    set_envs(root, 'certifi', {'dev'})
    check(root=root, sphinx='==1.0', certifi='==1.0', requests='==1.0', missed=['apiwrapper'], envs={'main'})


def test_very_deep_dependencies_reapply():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(Fake('1.0', 'c'), ),
        b=(Fake('1.0', 'c'), ),

        c=(Fake('1.0', 'd'), ),
        d=(Fake('1.0', 'e'), ),
        e=(Fake('1.0'), ),
    )
    set_envs(root, 'a', {'main'})
    set_envs(root, 'b', {'dev'})
    check(root=root, a='==1.0', c='==1.0', d='==1.0', e='==1.0', missed=['b'], envs={'main'})


def test_dependencies_unapply_twice_and_reapply():
    root = make_root(
        root=Fake('', 'requests', 'sphinx', 'certifi'),
        requests=(Fake('1.0', 'certifi'), ),
        sphinx=(Fake('1.0', 'requests'), ),
        certifi=(Fake('1.0'), ),
    )
    set_envs(root, 'sphinx', {'main'})
    set_envs(root, 'requests', {'dev'})
    set_envs(root, 'certifi', {'dev'})
    check(root=root, sphinx='==1.0', requests='==1.0', certifi='==1.0', missed=[], envs={'main'})


def test_direct_dependencies_without_resolving():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(Fake('1.0'), ),
        b=(Fake('1.0'), ),
    )
    set_envs(root, 'a', {'main'})
    set_envs(root, 'b', {'dev'})

    reqs = fast_filter(root)
    assert set(reqs) == {'a'}

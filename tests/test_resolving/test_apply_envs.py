# app
from ..helpers import Fake, check, make_root, set_envs


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

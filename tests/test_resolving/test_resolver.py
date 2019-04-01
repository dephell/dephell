# app
from ..helpers import Fake, check, make_root


def test_constraint_checks():
    root = make_root(
        root=Fake('', 'a', 'b<1.1'),
        a=(
            Fake('1.0'),
        ),
        b=(
            Fake('1.0'),
            Fake('1.1'),
        ),
    )
    check(root=root, a='==1.0', b='==1.0')


def test_more_complex_constraint():
    root = make_root(
        root=Fake('', 'a', 'b<=1.3,!=1.3,!=1.2'),
        a=(
            Fake('1.0'),
        ),
        b=(
            Fake('1.0'),
            Fake('1.1'),
            Fake('1.2'),
            Fake('1.3'),
        ),
    )
    check(root=root, a='==1.0', b='==1.1')


def test_all_have_constraints():
    root = make_root(
        root=Fake('', 'a', 'b<=1.3,!=1.3,!=1.2'),
        a=(
            Fake('1.0'),
        ),
        b=(
            Fake('1.0', 'a>=1.0', 'c>=1.0'),
        ),
        c=(
            Fake('1.0', 'a>=1.0'),
        ),
    )
    check(root=root, a='==1.0', b='==1.0')


def test_circular_dependency_on_older_version():
    root = make_root(
        root=Fake('', 'a>=1.0.0'),
        a=(
            Fake('1.0.0'),
            Fake('2.0.0', 'b==1.0.0'),
        ),
        b=(
            Fake('1.0.0', 'a==1.0.0'),
        ),
    )
    check(root=root, a='==1.0.0', missed=['b'])


def test_diamond_dependency_graph():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(
            Fake('1.0.0'),
            Fake('2.0.0', 'c==1.0.0'),
        ),
        b=(
            Fake('1.0.0', 'c==2.0.0'),
            Fake('2.0.0', 'c==3.0.0'),
        ),
        c=(
            Fake('1.0.0'),
            Fake('2.0.0'),
            Fake('3.0.0'),
        ),
    )
    check(root=root, a='==1.0.0', b='==2.0.0', c='==3.0.0')


def test_backjumps_after_partial_satisfier():
    root = make_root(
        root=Fake('', 'c', 'y==2'),
        a=(
            Fake('1', 'x>=1'),
        ),
        b=(
            Fake('1', 'x<2'),
        ),
        c=(
            Fake('1'),
            Fake('2', 'a', 'b'),
        ),
        x=(
            Fake('0'),
            Fake('1', 'y==1'),
            Fake('2'),
        ),
        y=(
            Fake('1'),
            Fake('2'),
        ),
    )
    check(root=root, c='==1', y='==2')


def test_rolls_back_leaf_versions_first():
    root = make_root(
        root=Fake('', 'a'),
        a=(
            Fake('1', 'b'),
            Fake('2', 'b', 'c==2'),
        ),
        b=(
            Fake('1'),
            Fake('2', 'c==1'),
        ),
        c=(
            Fake('1'),
            Fake('2'),
        ),
    )
    # now dephell choose first local maximum, not total.
    check(root=root)
    # check(root=root, a='==2', b='==1', c='==2')


def test_simple_transitive():
    root = make_root(
        root=Fake('', 'a'),
        a=(
            Fake('1', 'b==1'),
            Fake('2', 'b==2'),
            Fake('3', 'b==3'),
        ),
        b=(
            Fake('1', 'c'),
            Fake('2', 'c==2'),
            Fake('3', 'c==3'),
        ),
        c=(
            Fake('1'),
        ),
    )
    check(root=root, a='==1', b='==1', c='==1')


def test_backjump_to_nearer_unsatisfied_package():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(
            Fake('1', 'c==1'),
            Fake('2', 'c==2'),
        ),
        b=(
            Fake('1'),
            Fake('2'),
            Fake('3'),
        ),
        c=(
            Fake('1'),
        ),
    )
    check(root=root, a='==1', b='==3', c='==1')


def test_traverse_into_package_with_fewer_versions_first():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(
            Fake('1', 'c'),
            Fake('2', 'c'),
            Fake('3', 'c'),
            Fake('4', 'c'),
            Fake('5', 'c==1'),
        ),
        b=(
            Fake('1'),
            Fake('2'),
            Fake('3'),
            Fake('4', 'c==2'),
        ),
        c=(
            Fake('1'),
            Fake('2'),
        ),
    )
    check(root=root)
    # check(root=root, a='==4', b='==4', c='==2')


def test_backjump_past_failed_package_on_disjoint_constraint():
    root = make_root(
        root=Fake('', 'a', 'b>2'),
        a=(
            Fake('1', 'b'),
            Fake('2', 'b<1'),
        ),
        b=(
            Fake('2'),
            Fake('3'),
            Fake('4'),
        ),
    )
    check(root=root, a='==1', b='==4')


def test_cyclic_dependencies():
    root = make_root(
        root=Fake('', 'a'),
        a=(
            Fake('1', 'b==1'),
        ),
        b=(
            Fake('1', 'c==1'),
        ),
        c=(
            Fake('1', 'a==1'),
        ),
    )
    check(root=root, a='==1', b='==1', c='==1')


def test_cyclic_dependencies_with_unapply():
    root = make_root(
        root=Fake('', 'a'),
        a=(
            Fake('1', 'b==1'),
            Fake('2', 'b==2'),
        ),
        b=(
            Fake('1', 'c==1'),
            Fake('2', 'c==2'),
        ),
        c=(
            Fake('1', 'a==1'),
            Fake('2', 'b==2', 'a==1'),
        ),
    )
    check(root=root, a='==1', b='==1', c='==1')

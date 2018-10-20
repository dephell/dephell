from .factories import make_root, Fake, check


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
    check(root=root, a='==1.0.0', b='==1.0.0')


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

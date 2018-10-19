from .factories import make_deps


def test_make_deps():
    root = make_deps(
        root=dict(
            a='*',
            b='*',
        ),
        releases=dict(
            a=(1, 2, 3),
            b=(4, 5, 6),
        ),
        constraints=dict(
            a={
                '1': 'b>5',
                '2': 'b>5',
                '3': 'b>7',
            },
        ),
    )

    names = [dep.name for dep in root.dependencies]
    assert 'a' in names
    assert 'b' in names

# app
from .helpers import Fake, make_root


def test_make_deps():
    root = make_root(
        root=Fake('', 'a', 'b'),
        a=(
            Fake('1', 'b>5'),
            Fake('2', 'b>5'),
            Fake('3', 'b>7'),
        ),
        b=(
            Fake('4'),
            Fake('5'),
            Fake('6'),
        ),
    )

    names = [dep.name for dep in root.dependencies]
    assert 'a' in names
    assert 'b' in names

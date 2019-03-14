# app
from ..helpers import Fake, check, make_root


def test_extra():
    root = make_root(
        root=Fake('', 'a', 'b[sec]<1.1'),
        a=(
            Fake('1.0'),
        ),
        b=(
            Fake('1.0', extras=dict(sec=['c<=1.0'])),
            Fake('1.1'),
        ),
        c=(
            Fake('1.0'),
            Fake('1.1'),
        ),
        d=(
            Fake('1.0'),
            Fake('1.1'),
        ),
    )
    check(root=root, a='==1.0', b='==1.0', c='==1.0', missed=['d'])

import pytest

from dephell.converters import PIPConverter


@pytest.mark.parametrize('left, right, ok', [
    ('a>=3',    'a>=3',     True),
    ('a >= 3',  'a>=3',     True),
    ('a>=3',    'a>3',      False),
    (
        '-e git+git@github.com:dephell/dephell.git#egg=dephell',
        '-e git+git@github.com:dephell/dephell.git#egg=dephell',
        True,
    ),
    (
        '-e git+git@github.com:dephell/dephell.git#egg=dephell',
        '-e git+ssh://git@github.com:dephell/dephell.git#egg=dephell',
        True,
    ),
    (
        '-e git+git@github.com:dephell/dephell.git#egg=dephell',
        '-e git+git@github.com:dephell/dephell_discovery.git#egg=dephell',
        False,
    ),
])
def test_equal(left, right, ok):
    converter = PIPConverter(lock=False)
    dep_left = converter.loads(left).dependencies[0]
    dep_right = converter.loads(right).dependencies[0]

    dict_left = dep_left._get_comparable_dict(dep_left)
    dict_right = dep_right._get_comparable_dict(dep_right)
    assert (dict_left == dict_right) is ok

    equal = dep_left == dep_right
    assert equal is ok

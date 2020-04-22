# external
import pytest

# project
from dephell.converters import PIPConverter
from dephell.models import Requirement


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

    dict_left = Requirement._get_comparable_dict(dep_left)
    dict_right = Requirement._get_comparable_dict(dep_right)
    assert (dict_left == dict_right) is ok

    req_left = Requirement(dep=dep_left, lock=False)
    equal = req_left.same_dep(dep_right)
    assert equal is ok

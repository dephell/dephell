import pytest

from dephell_specifier import RangeSpecifier

# project
from dephell.utils import lazy_product, peppify_python


def test_lazy_product_order():
    result = list(lazy_product(range(3), range(3)))
    assert len(result) == 9
    expected = [
        (0, 0), (0, 1), (1, 0), (1, 1),
        (0, 2), (1, 2), (2, 0), (2, 1), (2, 2),
    ]
    assert result == expected


def test_lazy_product_tail():
    result = list(lazy_product([0], [1, 2]))
    assert len(result) == 2
    expected = [(0, 1), (0, 2)]
    assert result == expected


@pytest.mark.parametrize('spec, expected', [
    ('>=2.7',                   '>=2.7'),
    ('>=2.7,<3.4',              '>=2.7,<3.4'),
    ('==2.7.* || >=3.4',        '>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*'),
    ('==2.7.* || >=3.4,<3.8',   '>=2.7,<3.8,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*'),
])
def test_peppify_python(spec, expected):
    new = peppify_python(RangeSpecifier(spec))
    assert str(new) == str(RangeSpecifier(expected))

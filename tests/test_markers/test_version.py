# external
import pytest
from packaging.markers import Op, Value, Variable

# project
from dephell.markers.version import VersionMarker


@pytest.mark.parametrize('op, val, expected', [
    ('>=', '1.3', '>=1.3'),
    ('>', '1.3', '>1.3'),
    ('===', '1.3', '===1.3'),
    ('~=', '1.3', '~=1.3'),
])
def test_specifier(op, val, expected):
    m = VersionMarker(
        lhs=Variable('python_version'),
        op=Op(op),
        rhs=Value(val),
    )
    assert str(m.specifier) == expected


@pytest.mark.parametrize('val, op, expected', [
    ('1.3', '>=', '<=1.3'),
    ('1.3', '>', '<1.3'),
    ('1.3', '==', '==1.3'),
    ('1.3', '===', '===1.3'),
])
def test_swap(op, val, expected):
    m = VersionMarker(
        lhs=Value(val),
        op=Op(op),
        rhs=Variable('python_version'),
    )
    assert str(m.specifier) == expected


@pytest.mark.parametrize('left_op, left_val, right_op, right_val, result', [
    ('<', '1.2',    '<', '1.4',     '<1.2'),
    ('<=', '1.2',   '<', '1.4',     '<=1.2'),
    ('==', '1.2',   '<', '1.4',     '==1.2'),
    ('>=', '1.2',   '<=', '1.2',    '==1.2'),

    ('<=', '1.2',   '>=', '1.4',    None),
    ('<', '1.2',    '>', '1.2',     None),
])
def test_merge(left_op, left_val, right_op, right_val, result):
    lm = VersionMarker(
        lhs=Variable('python_version'),
        op=Op(left_op),
        rhs=Value(left_val),
    )
    rm = VersionMarker(
        lhs=Variable('python_version'),
        op=Op(right_op),
        rhs=Value(right_val),
    )
    if result is None:
        with pytest.raises(TypeError):
            lm + rm
    else:
        merged = lm + rm
        assert str(merged.specifier) == result

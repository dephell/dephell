import pytest
from packaging.markers import Variable, Op, Value
from dephell.markers.string import StringMarker


@pytest.mark.parametrize('op, val, expected', [
    ('==', 'posix', 'os_name == "posix"'),
])
def test_specifier(op, val, expected):
    m = StringMarker(
        lhs=Variable('os_name'),
        op=Op(op),
        rhs=Value(val),
    )
    assert str(m) == expected


@pytest.mark.parametrize('left_op, left_val, right_op, right_val, result', [
    ('==', 'posix',     '==', 'posix',  'os_name == "posix"'),
    ('==', 'posix',     '>=', 'posix',  'os_name == "posix"'),
    ('==', 'posix',     '<=', 'posix',  'os_name == "posix"'),
    ('<=', 'posix',     '==', 'posix',  'os_name == "posix"'),
    ('>=', 'posix',     '<=', 'posix',  'os_name == "posix"'),

    ('>', 'posix',      '<', 'posix',   None),
    ('==', 'posix',     '==', 'win',    None),
])
def test_merge(left_op, left_val, right_op, right_val, result):
    lm = StringMarker(
        lhs=Variable('os_name'),
        op=Op(left_op),
        rhs=Value(left_val),
    )
    rm = StringMarker(
        lhs=Variable('os_name'),
        op=Op(right_op),
        rhs=Value(right_val),
    )
    if result is None:
        with pytest.raises(TypeError):
            lm + rm
    else:
        merged = lm + rm
        assert str(merged) == result

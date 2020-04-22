# external
import pytest

# project
from dephell.actions._json import _flatdict


@pytest.mark.parametrize('given, expected', [
    (1, 1),
    ({1: 2}, {'1': 2}),
    ({1: {2: 3}}, {'1.2': 3}),
    ({1: {2: 3, 4: 5}}, {'1.2': 3, '1.4': 5}),
    ({1: {2: 3, 4: 5}, 6: 7}, {'1.2': 3, '1.4': 5, '6': 7}),
    ([{1: {2: 3}}, {4: {5: 6}}], [{'1.2': 3}, {'4.5': 6}]),
])
def test_flatdict(given, expected):
    assert _flatdict(given) == expected

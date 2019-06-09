# project
from dephell.controllers._mutator import lazy_product


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

# external
import pytest

# project
from dephell.actions import arabic2roman, roman2arabic


@pytest.mark.parametrize('arabic, roman', [
    (1, 'I'),
    (2, 'II'),
    (3, 'III'),
    (4, 'IV'),
    (5, 'V'),
    (6, 'VI'),
    (7, 'VII'),

    (10, 'X'),
    (13, 'XIII'),
    (14, 'XIV'),
    (15, 'XV'),
    (16, 'XVI'),

    (20, 'XX'),
    (24, 'XXIV'),
    (25, 'XXV'),
    (26, 'XXVI'),

    (994, 'CMXCIV'),
    (1995, 'MCMXCV'),
    (2015, 'MMXV'),
    (3986, 'MMMCMLXXXVI'),
])
def test_roman(arabic, roman):
    assert arabic2roman(arabic) == roman
    assert roman2arabic(roman) == arabic

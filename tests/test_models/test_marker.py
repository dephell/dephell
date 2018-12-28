import pytest

from dephell.models.marker import Markers


@pytest.mark.parametrize('marker, value', [
    ('python_version == "2.4"', '==2.4'),
    ('python_version >= "2.4" and python_version <= "2.7"', '>=2.4,<=2.7'),
    ('python_version >= "2.4" or python_version <= "2.7"', '>=2.4 || <=2.7'),
])
def test_get_variable(marker, value):
    m = Markers(marker)
    v = m._get_variable(name='python_version')
    assert v == value

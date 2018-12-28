import pytest

from dephell.models.marker import Markers


@pytest.mark.parametrize('marker, value', [
    ('python_version == "2.4"', '==2.4'),
    ('python_version >= "2.4" and python_version <= "2.7"', '>=2.4,<=2.7'),
    ('python_version >= "2.4" or python_version <= "2.7"', '>=2.4 || <=2.7'),
    ('python_version == "2.4" and os_name == "linux"', '==2.4'),

    # `or` contains different marker
    ('python_version == "2.4" or os_name == "linux"', None),
    # no needed marker
    ('os_name == "linux"', None),
])
def test_get_variable(marker, value):
    m = Markers(marker)
    v = m._get_variable(name='python_version')
    assert v == value


def test_python_version():
    m = Markers('python_version >= "2.4" and python_version <= "2.7"')
    v = m.python_version
    assert '2.4' in v
    assert '2.5' in v
    assert '2.3' not in v
    assert '3.4' not in v

import pytest

from dephell.markers import Markers


@pytest.mark.parametrize('marker, value', [
    ('os_name == "posix"', 'posix'),
    ('os_name == "posix" and os_name == "posix"', 'posix'),
    ('os_name == "posix" or os_name == "posix"', 'posix'),
    ('os_name == "posix" and python_version >= "2.7"', 'posix'),

    ('os_name == "posix" and os_name == "nt"', None),
    ('os_name == "posix" or python_version >= "2.7"', None),
])
def test_get_string(marker, value):
    m = Markers(marker)
    v = m.get_string(name='os_name')
    assert v == value


@pytest.mark.parametrize('marker, value', [
    ('python_version == "2.4"', '==2.4'),
    ('python_version >= "2.4" and python_version <= "2.7"', '<=2.7,>=2.4'),
    ('python_version >= "2.4" or python_version <= "2.7"', '<=2.7 || >=2.4'),
    ('python_version == "2.4" and os_name == "linux"', '==2.4'),

    # `or` contains different marker
    ('python_version == "2.4" or os_name == "linux"', None),
    # no needed marker
    ('os_name == "linux"', None),
])
def test_get_version(marker, value):
    m = Markers(marker)
    v = m.get_version(name='python_version')
    assert v == value


def test_python_version():
    m = Markers('python_version >= "2.4" and python_version <= "2.7"')
    v = m.python_version
    assert '2.4' in v
    assert '2.5' in v
    assert '2.3' not in v
    assert '3.4' not in v


def test_add_python_version():
    m = Markers('python_version >= "2.4"')
    assert '3.2' in m.python_version
    m.add(name='python_version', operator='<=', value='2.7')
    v = m.python_version
    assert '2.4' in v
    assert '2.5' in v
    assert '2.3' not in v
    assert '3.4' not in v


@pytest.mark.parametrize('given, expected', [
    (
        'python_version >= "2.4" and python_version <= "2.7"',
        'python_version>=2.4 and python_version<=2.7',
    ),
    (
        '(python_version >= "2.4" and python_version <= "2.7")',
        'python_version>=2.4 and python_version<=2.7',
    ),
    (
        '(python_version >= "2.4" or python_version <= "2.7") or os_name == "linux"',
        'python_version>=2.4 or python_version<=2.7 or os_name == "linux"',
    ),
    (
        '(python_version >= "2.4" and python_version <= "2.7") or os_name == "linux"',
        'python_version>=2.4 and python_version<=2.7 or os_name == "linux"',
    ),
])
def test_str(given, expected):
    m = Markers(given)
    assert str(m) == expected

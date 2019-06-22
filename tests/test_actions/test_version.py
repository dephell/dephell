# external
import pytest

# project
from dephell.actions import bump_file, get_version_from_file


@pytest.mark.parametrize('old, new, changed, content, expected', [
    (
        '1.2', '1.3', True,
        ('from a import b', 'c = "1.2"', '__version__ = "1.2"'),
        ('from a import b', 'c = "1.2"', '__version__ = "1.3"'),
    ),
    (
        'III', 'IV', True,
        ('from a import b', 'c = "1.2"', '__version__ = "III"'),
        ('from a import b', 'c = "1.2"', '__version__ = "IV"'),
    ),
    (
        '1.2', '1.3', True,
        ('from a import b', 'c = "1.2"', '__version__ = "1.0"'),
        ('from a import b', 'c = "1.2"', '__version__ = "1.3"'),
    ),
])
def test_bump_file(old, new, changed, content, expected, temp_path):
    path = temp_path / '__init__.py'
    path.write_text('\n'.join(content))
    assert bump_file(path=path, old=old, new=new) is changed
    assert list(path.read_text().split('\n')) == list(expected)


@pytest.mark.parametrize('expected, content', [
    ('1.2', ('from a import b', 'c = "1.1"', '__version__ = "1.2"')),
])
def test_get_version_from_file(expected, content, temp_path):
    path = temp_path / '__init__.py'
    path.write_text('\n'.join(content))
    found = get_version_from_file(path=path)
    assert found == expected

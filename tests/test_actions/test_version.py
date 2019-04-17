# external
import pytest

# project
from dephell.actions import bump_file, bump_version, get_version_from_file


@pytest.mark.parametrize('scheme, rule, old, new', [
    # pep base version
    ('pep', 'major',    '1.2.3', '2.0.0'),
    ('pep', 'minor',    '1.2.3', '1.3.0'),
    ('pep', 'patch',    '1.2.3', '1.2.4'),

    # semver base version
    ('semver', 'major', '1.2.3', '2.0.0'),
    ('semver', 'minor', '1.2.3', '1.3.0'),
    ('semver', 'patch', '1.2.3', '1.2.4'),

    # comver base version
    ('comver', 'major', '1.2', '2.0'),
    ('comver', 'minor', '1.2', '1.3'),

    # pep add special part
    ('pep', 'pre',      '1.2.3', '1.2.3rc1'),
    ('pep', 'post',     '1.2.3', '1.2.3.post1'),
    ('pep', 'dev',      '1.2.3', '1.2.4.dev1'),
    ('pep', 'local',    '1.2.3', '1.2.4+1'),

    # pep bump special part
    ('pep', 'pre',      '1.2.3rc1', '1.2.3rc2'),
    ('pep', 'post',     '1.2.3.post1', '1.2.3.post2'),
    ('pep', 'dev',      '1.2.3.dev1', '1.2.4.dev2'),
    ('pep', 'local',    '1.2.3+1', '1.2.4+2'),

    # semver add special part
    ('semver', 'pre',   '1.2.3', '1.2.3-rc.1'),
    ('semver', 'local', '1.2.3', '1.2.4+1'),

    # semver bump special part
    ('semver', 'pre',   '1.2.3-rc.1', '1.2.3-rc.2'),
    ('semver', 'local', '1.2.3+1', '1.2.4+2'),

    # roman versioning
    ('roman', 'major',  'X', 'XI'),
    ('roman', 'major',  'XII', 'XIV'),
])
def test_bump_version(scheme, rule, old, new):
    bump_version(scheme=scheme, rule=rule, version=old) == new


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

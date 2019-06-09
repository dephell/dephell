# external
import pytest

# project
from dephell.actions import bump_file, bump_version, get_version_from_file


@pytest.mark.parametrize('scheme, rule, old, new', [
    # pep base version
    ('pep', 'major',    '1.2.3', '2.0.0'),
    ('pep', 'minor',    '1.2.3', '1.3.0'),
    ('pep', 'patch',    '1.2.3', '1.2.4'),

    # pep pre-base version
    ('pep', 'premajor', '1.2.3', '2.0.0rc1'),
    ('pep', 'preminor', '1.2.3', '1.3.0rc1'),
    ('pep', 'prepatch', '1.2.3', '1.2.4rc1'),

    # semver base version
    ('semver', 'major', '1.2.3', '2.0.0'),
    ('semver', 'minor', '1.2.3', '1.3.0'),
    ('semver', 'patch', '1.2.3', '1.2.4'),

    # semver pre-base version
    ('semver', 'premajor', '1.2.3', '2.0.0-rc.1'),
    ('semver', 'preminor', '1.2.3', '1.3.0-rc.1'),
    ('semver', 'prepatch', '1.2.3', '1.2.4-rc.1'),

    # comver base version
    ('comver', 'major', '1.2', '2.0'),
    ('comver', 'minor', '1.2', '1.3'),

    # comver special
    ('comver', 'premajor',  '1.2',      '2.0-rc.1'),
    ('comver', 'preminor',  '1.2',      '1.3-rc.1'),
    ('comver', 'pre',       '1.2',      '1.2-rc.1'),
    ('comver', 'local',     '1.2',      '1.2+1'),
    ('comver', 'pre',       '1.2-rc.1', '1.2-rc.2'),
    ('comver', 'local',     '1.2+1',    '1.2+2'),
    ('comver', 'release',   '1.2-rc.1', '1.2'),
    ('comver', 'release',   '1.2+1',    '1.2'),

    # romver base version
    ('romver', 'major', '1.2.0', '2.0.0'),
    ('romver', 'minor', '1.2.0', '1.3.0'),

    # romver special
    ('romver', 'premajor',  '1.2.0',      '2.0.0-rc.1'),
    ('romver', 'preminor',  '1.2.0',      '1.3.0-rc.1'),
    ('romver', 'pre',       '1.2.0',      '1.2.0-rc.1'),
    ('romver', 'pre',       '1.2.0-rc.1', '1.2.0-rc.2'),
    ('romver', 'release',   '1.2.0-rc.1', '1.2.0'),

    # pep add special part
    ('pep', 'pre',      '1.2.3', '1.2.3rc1'),
    ('pep', 'post',     '1.2.3', '1.2.3.post1'),
    ('pep', 'dev',      '1.2.3', '1.2.3.dev1'),
    ('pep', 'local',    '1.2.3', '1.2.3+1'),

    # pep bump special part
    ('pep', 'pre',      '1.2.3rc1', '1.2.3rc2'),
    ('pep', 'post',     '1.2.3.post1', '1.2.3.post2'),
    ('pep', 'dev',      '1.2.3.dev1', '1.2.3.dev2'),
    ('pep', 'local',    '1.2.3+1', '1.2.3+2'),

    # pep release
    ('pep', 'release', '1.2.3rc1', '1.2.3'),
    ('pep', 'release', '1.2.3.post1', '1.2.3.post1'),
    ('pep', 'release', '1.2.3.dev1', '1.2.3.dev1'),
    ('pep', 'release', '1.2.3+1', '1.2.3'),

    # semver add special part
    ('semver', 'pre',   '1.2.3', '1.2.3-rc.1'),
    ('semver', 'local', '1.2.3', '1.2.3+1'),

    # semver bump special part
    ('semver', 'pre',   '1.2.3-rc.1', '1.2.3-rc.2'),
    ('semver', 'local', '1.2.3+1', '1.2.3+2'),

    # semver release
    ('semver', 'release', '1.2.3', '1.2.3'),
    ('semver', 'release', '1.2.3-rc.1', '1.2.3'),
    ('semver', 'release', '1.2.3+1', '1.2.3'),
    ('semver', 'release', '1.2.3-rc.1+1', '1.2.3'),

    # roman versioning
    ('roman', 'major',  'X', 'XI'),
    ('roman', 'major',  'XII', 'XIII'),
])
def test_bump_version(scheme, rule, old, new):
    assert bump_version(scheme=scheme, rule=rule, version=old) == new


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

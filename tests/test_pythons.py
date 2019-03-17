# external
import pytest
from packaging.version import Version

# project
from dephell.pythons import Pythons


def test_abstract():
    manager = Pythons(abstract=True)
    pythons = {'.'.join(map(str, p.version.release[:2])): p for p in manager}
    assert len({'2.7', '3.5', '3.7'} - set(pythons)) == 0
    assert pythons['2.6'].abstract is True
    assert pythons['3.0'].abstract is True
    assert not all(p.abstract for p in manager)


@pytest.mark.parametrize('version', [
    '2.7',
    '3.0',
    '3.4',
    '3.5',
    '3.6',
    '3.7',
])
def test_get_by_version(version):
    manager = Pythons(abstract=True)
    python = manager.get_by_version(Version(version))
    assert str(python.version).startswith(version)

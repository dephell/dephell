import pytest
from dephell.controllers import DependencyMaker
from dephell.models import RootDependency
from dephell.repositories.warehouse._simple import SimpleWareHouseRepo


@pytest.mark.parametrize('fname, name, version', [
    ('dephell-0.7.3-py3-none-any.whl', 'dephell', '0.7.3'),
    ('dephell-0.7.3.tar.gz', 'dephell', '0.7.3'),

    ('flake8_commas-2.0.0-py2.py3-none-any.whl', 'flake8_commas', '2.0.0'),
    ('flake8-commas-2.0.0.tar.gz ', 'flake8-commas', '2.0.0'),
])
def test_parse_name(fname, name, version):
    assert SimpleWareHouseRepo._parse_name(fname) == (name, version)


def test_get_releases():
    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='dephell')[0]
    repo = SimpleWareHouseRepo()
    releases = repo.get_releases(dep=dep)
    releases = {str(r.version): r for r in releases}
    assert '0.7.0' in set(releases)
    assert str(releases['0.7.0'].python) == '>=3.5'
    assert len(releases['0.7.0'].hashes) == 2

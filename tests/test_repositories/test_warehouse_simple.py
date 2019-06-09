import asyncio

import pytest

from dephell.constants import DEFAULT_WAREHOUSE
from dephell.controllers import DependencyMaker
from dephell.models import RootDependency
from dephell.repositories import WarehouseSimpleRepo


loop = asyncio.get_event_loop()


@pytest.mark.parametrize('fname, name, version', [
    ('dephell-0.7.3-py3-none-any.whl', 'dephell', '0.7.3'),
    ('dephell-0.7.3.tar.gz', 'dephell', '0.7.3'),

    ('flake8_commas-2.0.0-py2.py3-none-any.whl', 'flake8_commas', '2.0.0'),
    ('flake8-commas-2.0.0.tar.gz ', 'flake8-commas', '2.0.0'),
])
def test_parse_name(fname, name, version):
    assert WarehouseSimpleRepo._parse_name(fname) == (name, version)


def test_get_releases():
    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='dephell')[0]
    repo = WarehouseSimpleRepo(name='pypi', url=DEFAULT_WAREHOUSE)
    releases = repo.get_releases(dep=dep)
    releases = {str(r.version): r for r in releases}
    assert '0.7.0' in set(releases)
    assert str(releases['0.7.0'].python) == '>=3.5'
    assert len(releases['0.7.0'].hashes) == 2


def test_extra():
    repo = WarehouseSimpleRepo(name='pypi', url=DEFAULT_WAREHOUSE)

    coroutine = repo.get_dependencies(name='requests', version='2.21.0')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}
    assert 'chardet' in deps
    assert 'cryptography' not in deps
    assert 'win-inet-pton' not in deps

    coroutine = repo.get_dependencies(name='requests', version='2.21.0', extra='security')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}
    assert 'chardet' not in deps
    assert 'win-inet-pton' not in deps
    assert 'cryptography' in deps

import asyncio

import pytest

from dephell.constants import DEFAULT_WAREHOUSE
from dephell.controllers import DependencyMaker
from dephell.models import Auth, RootDependency
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


@pytest.mark.allow_hosts()
def test_get_releases():
    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='dephell')[0]
    repo = WarehouseSimpleRepo(name='pypi', url=DEFAULT_WAREHOUSE)
    releases = repo.get_releases(dep=dep)
    releases = {str(r.version): r for r in releases}
    assert '0.7.0' in set(releases)
    assert str(releases['0.7.0'].python) == '>=3.5'
    assert len(releases['0.7.0'].hashes) == 2


@pytest.mark.allow_hosts()
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


def test_get_releases_mocked(requests_mock, temp_cache, fixtures_path):
    url = 'https://artifactory.example.org/pypi/'
    text = (fixtures_path / 'warehouse-simple.html').read_text()
    requests_mock.get(url + 'dephell-shells/', text=text)

    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='dephell-shells')[0]
    repo = WarehouseSimpleRepo(name='pypi', url=url)
    releases = repo.get_releases(dep=dep)

    assert requests_mock.call_count == 1
    assert len(releases) == 4


def test_get_releases_auth(requests_mock, temp_cache, fixtures_path):
    url = 'https://artifactory.example.org/pypi/'
    text = (fixtures_path / 'warehouse-simple.html').read_text()
    requests_mock.get(url + 'dephell-shells/', text=text)

    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='dephell-shells')[0]
    auth = Auth(
        hostname='artifactory.example.org',
        username='gram',
        password='test',
    )
    repo = WarehouseSimpleRepo(name='pypi', url=url, auth=auth)
    releases = repo.get_releases(dep=dep)

    assert requests_mock.call_count == 1
    assert len(releases) == 4
    assert requests_mock.last_request.headers['Authorization'] == 'Basic Z3JhbTp0ZXN0'


@pytest.mark.allow_hosts()  # to download archive
def test_get_deps(requests_mock, temp_cache, fixtures_path):
    url = 'https://custom.pypi.org/'
    text = (fixtures_path / 'warehouse-simple.html').read_text()
    requests_mock.get(url + 'dephell-shells/', text=text)

    repo = WarehouseSimpleRepo(name='pypi', url=url)
    coroutine = repo.get_dependencies(name='dephell-shells', version='0.1.2')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}
    assert set(deps) == {'attrs', 'pexpect', 'shellingham'}
    assert requests_mock.call_count == 1


@pytest.mark.allow_hosts()  # to download archive
def test_get_deps_auth(requests_mock, temp_cache, fixtures_path):
    url = 'https://custom.pypi.org/'
    text = (fixtures_path / 'warehouse-simple.html').read_text()
    requests_mock.get(url + 'dephell-shells/', text=text)

    auth = Auth(
        hostname='custom.pypi.org',
        username='gram',
        password='test',
    )
    repo = WarehouseSimpleRepo(name='pypi', url=url, auth=auth)
    coroutine = repo.get_dependencies(name='dephell-shells', version='0.1.2')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}

    assert set(deps) == {'attrs', 'pexpect', 'shellingham'}
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.headers['Authorization'] == 'Basic Z3JhbTp0ZXN0'

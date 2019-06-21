# built-in
import asyncio
import json
from pathlib import Path

import pytest

# project
from dephell.constants import DEFAULT_WAREHOUSE
from dephell.controllers import DependencyMaker
from dephell.models import RootDependency, Auth
from dephell.repositories import WarehouseAPIRepo


loop = asyncio.get_event_loop()


@pytest.mark.allow_hosts()
def test_extra():
    repo = WarehouseAPIRepo(name='pypi', url=DEFAULT_WAREHOUSE)

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


@pytest.mark.allow_hosts()
def test_info_from_files():
    repo = WarehouseAPIRepo(name='pypi', url=DEFAULT_WAREHOUSE)
    coroutine = repo.get_dependencies(name='m2r', version='0.2.1')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}
    assert set(deps) == {'mistune', 'docutils'}


def test_get_releases(requests_mock, temp_cache, fixtures_path: Path):
    url = 'https://pypi.org/pypi/'
    text = (fixtures_path / 'warehouse-api-package.json').read_text()
    requests_mock.get(url + 'dephell-shells/json', text=text)

    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='dephell-shells')[0]
    repo = WarehouseAPIRepo(name='pypi', url=url)
    releases = repo.get_releases(dep=dep)

    assert requests_mock.call_count == 1
    assert len(releases) == 4


def test_get_releases_auth(requests_mock, temp_cache, fixtures_path: Path):
    url = 'https://custom.pypi.org/pypi/'
    text = (fixtures_path / 'warehouse-api-package.json').read_text()
    requests_mock.get(url + 'dephell-shells/json', text=text)

    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='dephell-shells')[0]
    repo = WarehouseAPIRepo(name='pypi', url=url, auth=Auth(
        hostname='custom.pypi.org',
        username='gram',
        password='test',
    ))
    releases = repo.get_releases(dep=dep)

    assert requests_mock.call_count == 1
    assert len(releases) == 4
    assert requests_mock.last_request.headers['Authorization'] == 'Basic Z3JhbTp0ZXN0'


def test_get_deps(asyncio_mock, temp_cache, fixtures_path: Path):
    url = 'https://custom.pypi.org/pypi/'
    text = (fixtures_path / 'warehouse-api-release.json').read_text()
    asyncio_mock.get(url + 'dephell-shells/0.1.2/json', body=text)

    repo = WarehouseAPIRepo(name='pypi', url=url)
    coroutine = repo.get_dependencies(name='dephell-shells', version='0.1.2')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}
    assert set(deps) == {'attrs', 'pexpect', 'shellingham'}


def test_get_deps_auth(asyncio_mock, temp_cache, fixtures_path: Path):
    url = 'https://custom.pypi.org/pypi/'
    text = (fixtures_path / 'warehouse-api-release.json').read_text()
    asyncio_mock.get(url + 'dephell-shells/0.1.2/json', body=text)

    auth = Auth(
        hostname='custom.pypi.org',
        username='gram',
        password='test',
    )
    repo = WarehouseAPIRepo(name='pypi', url=url, auth=auth)
    coroutine = repo.get_dependencies(name='dephell-shells', version='0.1.2')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}

    assert set(deps) == {'attrs', 'pexpect', 'shellingham'}
    assert len(asyncio_mock.requests) == 1
    client = list(asyncio_mock.requests.values())[0][0].args[0]
    assert client._default_headers['authorization'] == 'Basic Z3JhbTp0ZXN0'


def test_download(asyncio_mock, temp_cache, fixtures_path: Path, temp_path: Path,
                  requirements_dir: Path):
    pypi_url = 'https://custom.pypi.org/pypi/'
    json_response = (fixtures_path / 'warehouse-api-release.json').read_text()
    json_content = json.loads(json_response)
    file_url = json_content['urls'][0]['url']
    file_name = json_content['urls'][0]['filename']
    file_content = (requirements_dir / 'wheel.whl').read_bytes()

    asyncio_mock.get(pypi_url + 'dephell-shells/0.1.2/json', body=json_response)
    asyncio_mock.get(file_url, body=file_content)

    repo = WarehouseAPIRepo(name='pypi', url=pypi_url)
    coroutine = repo.download(name='dephell-shells', version='0.1.2', path=temp_path)
    result = loop.run_until_complete(asyncio.gather(coroutine))[0]
    assert result is True
    assert (temp_path / file_name).exists()
    assert (temp_path / file_name).read_bytes() == file_content

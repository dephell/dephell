# built-in
import asyncio

# project
from dephell.repositories import WareHouseRepo


loop = asyncio.get_event_loop()


def test_extra():
    repo = WareHouseRepo()

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


def test_info_from_files():
    repo = WareHouseRepo()
    coroutine = repo.get_dependencies(name='m2r', version='0.2.1')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}
    assert set(deps) == {'mistune', 'docutils'}

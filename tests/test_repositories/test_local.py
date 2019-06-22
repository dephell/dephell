# built-in
import asyncio
from pathlib import Path

# project
from dephell.repositories import LocalRepo


loop = asyncio.get_event_loop()


def test_root_file():
    repo = LocalRepo(Path('tests') / 'requirements' / 'setup.py')
    root = repo.get_root(name='dephell', version='0.2.0')
    assert root.name == 'dephell'
    assert root.version == '0.2.0'
    assert root.description == 'Dependency resolution for Python'


def test_root_dir():
    repo = LocalRepo(Path('tests') / 'requirements' / 'egg-info')
    root = repo.get_root(name='dephell', version='0.2.0')
    assert root.name == 'dephell'
    assert root.version == '0.2.1'
    assert root.links['home'] == 'https://github.com/orsinium/dephell'


def test_deps_file():
    repo = LocalRepo(Path('tests') / 'requirements' / 'setup.py')
    coroutine = repo.get_dependencies(name='dephell', version='0.2.0')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}
    expected = {'attrs', 'cached-property', 'packaging', 'requests', 'colorama', 'libtest'}
    assert set(deps) == expected

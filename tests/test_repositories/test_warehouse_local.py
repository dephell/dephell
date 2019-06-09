# built-in
import asyncio
from pathlib import Path

# project
from dephell.repositories import WarehouseLocalRepo
from dephell.controllers import DependencyMaker
from dephell.models import RootDependency


loop = asyncio.get_event_loop()


def test_get_releases():
    repo = WarehouseLocalRepo(name='pypi', path=Path('tests', 'repository'))
    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='dephell-discover')[0]
    releases = repo.get_releases(dep=dep)
    releases = {str(r.version): r for r in releases}
    assert set(releases) == {'0.2.4', '0.2.5'}


def test_get_dependencies():
    repo = WarehouseLocalRepo(name='pypi', path=Path('tests', 'repository'))

    coroutine = repo.get_dependencies(name='dephell-discover', version='0.2.4')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    deps = {dep.name: dep for dep in deps}
    assert set(deps) == {'attrs'}

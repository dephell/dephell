# project
# external
import attr
import pytest

from dephell import converters
from dephell.controllers import Graph
from dephell.models import Requirement
from dephell.repositories import WareHouseRepo


@pytest.mark.parametrize('converter, path', [
    (converters.PIPConverter(lock=False), './tests/requirements/attrs-requests.txt'),
    (converters.PIPConverter(lock=False), './tests/requirements/django-deal.txt'),
    (converters.PIPConverter(lock=False), './tests/requirements/scipy-pandas-numpy.txt'),

    (converters.PIPFileConverter(), './tests/requirements/pipfile.toml'),
    (converters.PIPFileLockConverter(), './tests/requirements/pipfile.lock.json'),

    (converters.PoetryConverter(), './tests/requirements/poetry.toml'),
    (converters.PoetryLockConverter(), './tests/requirements/poetry.lock.toml'),

    (converters.SetupPyConverter(), './tests/requirements/setup.py'),
    (converters.EggInfoConverter(), './tests/requirements/egg-info/'),
    (converters.WheelConverter(), './tests/requirements/wheel.whl'),
])
def test_load_dump_load_deps(converter, path):
    root1 = converter.load(path)
    reqs1 = Requirement.from_graph(graph=Graph(root1), lock=False)

    content = converter.dumps(reqs1, project=root1)
    root2 = converter.loads(content)
    reqs2 = Requirement.from_graph(graph=Graph(root2), lock=False)

    map1 = {req.name: req for req in reqs1}
    map2 = {req.name: req for req in reqs2}
    assert set(map1) == set(map2), 'loaded and dumped different deps set'

    # check all params
    exclude = {'sources', 'description'}
    for name, req1 in map1.items():
        req2 = map2[name]
        d1 = {k: v for k, v in req1 if k not in exclude}
        d2 = {k: v for k, v in req2 if k not in exclude}
        assert d1 == d2

    # check warehouse URL
    for name, req1 in map1.items():
        req2 = map2[name]
        if isinstance(req1.dep.repo, WareHouseRepo):
            assert req1.dep.repo.name == req2.dep.repo.name
            assert req1.dep.repo.url == req2.dep.repo.url

    # exactly one dev or main env should be specified for dep
    for name, req1 in map1.items():
        req2 = map2[name]
        assert req1.is_dev is not req1.is_main
        assert req2.is_dev is not req2.is_main

    # check envs (extras)
    for name, req1 in map1.items():
        req2 = map2[name]
        assert req1.dep.envs == req2.dep.envs


@pytest.mark.parametrize('converter, path, exclude', [
    (converters.PIPFileConverter(), './tests/requirements/pipfile.toml', ['raw_name']),
    (converters.PIPFileLockConverter(), './tests/requirements/pipfile.lock.json', ['raw_name']),

    (converters.PoetryConverter(), './tests/requirements/poetry.toml', []),
    (converters.PoetryLockConverter(), './tests/requirements/poetry.lock.toml', []),

    (converters.SetupPyConverter(), './tests/requirements/setup.py', []),
    (converters.EggInfoConverter(), './tests/requirements/egg-info/', ['package', 'entrypoints']),
    (converters.WheelConverter(), './tests/requirements/wheel.whl', ['package', 'entrypoints']),
])
def test_load_dump_load_metainfo(converter, path, exclude):
    root1 = converter.load(path)
    reqs1 = Requirement.from_graph(graph=Graph(root1), lock=False)

    content = converter.dumps(reqs1, project=root1)
    root2 = converter.loads(content)

    root1.dependencies = None
    root2.dependencies = None
    for field in exclude:
        setattr(root1, field, None)
        setattr(root2, field, None)
    assert attr.asdict(root1) == attr.asdict(root2)

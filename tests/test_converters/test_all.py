# external
# built-in
from pathlib import Path

import attr
import pytest

# project
from dephell import converters
from dephell.controllers import DependencyMaker, Graph, RepositoriesRegistry
from dephell.models import Requirement, RootDependency


root_path = Path(__file__).parent.parent / 'requirements'


@pytest.mark.allow_hosts()
@pytest.mark.parametrize('converter, path', [
    (converters.PIPConverter(lock=False), root_path / 'attrs-requests.txt'),
    (converters.PIPConverter(lock=False), root_path / 'django-deal.txt'),
    (converters.PIPConverter(lock=False), root_path / 'scipy-pandas-numpy.txt'),

    (converters.PIPFileConverter(), root_path / 'pipfile.toml'),
    (converters.PIPFileLockConverter(), root_path / 'pipfile.lock.json'),

    (converters.FlitConverter(), root_path / 'flit.toml'),

    (converters.PoetryConverter(), root_path / 'poetry.toml'),
    (converters.PoetryLockConverter(), root_path / 'poetry.lock.toml'),

    (converters.SetupPyConverter(), root_path / 'setup.py'),
    (converters.EggInfoConverter(), root_path / 'egg-info'),
    (converters.WheelConverter(), root_path / 'wheel.whl'),
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
    if isinstance(converter, converters.EggInfoConverter):
        exclude.add('git')
    for name, req1 in map1.items():
        req2 = map2[name]
        d1 = {k: v for k, v in req1 if k not in exclude}
        d2 = {k: v for k, v in req2 if k not in exclude}
        assert d1 == d2

    # check warehouse URL
    for name, req1 in map1.items():
        req2 = map2[name]
        if isinstance(req1.dep.repo, RepositoriesRegistry):
            assert len(req1.dep.repo.repos) == len(req2.dep.repo.repos)
            for repo1, repo2 in zip(req1.dep.repo.repos, req2.dep.repo.repos):
                assert repo1.name == repo2.name
                assert repo1.url == repo2.url

    # exactly one dev or main env should be specified for dep
    for name, req1 in map1.items():
        req2 = map2[name]
        assert req1.is_dev is not req1.is_main
        assert req2.is_dev is not req2.is_main

    # check envs (extras)
    for name, req1 in map1.items():
        req2 = map2[name]
        assert req1.dep.envs == req2.dep.envs


@pytest.mark.allow_hosts()
@pytest.mark.parametrize('converter, path, exclude', [
    (
        converters.PIPFileConverter(),
        root_path / 'pipfile.toml',
        ['raw_name'],
    ),
    (
        converters.PIPFileLockConverter(),
        root_path / 'pipfile.lock.json',
        ['raw_name', 'python'],
    ),
    (converters.FlitConverter(), root_path / 'flit.toml', []),
    (converters.PoetryConverter(), root_path / 'poetry.toml', []),
    (converters.PoetryLockConverter(), root_path / 'poetry.lock.toml', []),
    (converters.SetupPyConverter(), root_path / 'setup.py', []),
    (
        converters.EggInfoConverter(),
        root_path / 'egg-info',
        ['package', 'entrypoints', 'readme'],
    ),
    (
        converters.WheelConverter(),
        root_path / 'wheel.whl',
        ['package', 'entrypoints'],
    ),
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


@pytest.mark.allow_hosts()
@pytest.mark.parametrize('converter, path', [
    (converters.PIPConverter(lock=False), root_path / 'attrs-requests.txt'),
    (converters.PIPConverter(lock=False), root_path / 'django-deal.txt'),
    (converters.PIPConverter(lock=False), root_path / 'scipy-pandas-numpy.txt'),

    (converters.PIPFileConverter(), root_path / 'pipfile.toml'),
    (converters.PIPFileLockConverter(), root_path / 'pipfile.lock.json'),

    (converters.FlitConverter(), root_path / 'flit.toml'),

    (converters.PoetryConverter(), root_path / 'poetry.toml'),
    # (converters.PoetryLockConverter(), root_path / 'poetry.lock.toml'),

    (converters.SetupPyConverter(), root_path / 'setup.py'),
    (converters.EggInfoConverter(), root_path / 'egg-info' / 'PKG-INFO'),
    (converters.WheelConverter(), root_path / 'wheel.whl'),
])
def test_idempotency(converter, path):
    root1 = converter.load(path)
    reqs1 = Requirement.from_graph(graph=Graph(root1), lock=False)

    content1 = converter.dumps(reqs1, project=root1)

    root2 = converter.loads(content1)
    reqs2 = Requirement.from_graph(graph=Graph(root2), lock=False)

    content2 = converter.dumps(reqs2, project=root2, content=content1)

    assert content1 == content2


@pytest.mark.allow_hosts()
@pytest.mark.parametrize('converter', [
    # converters.PIPConverter(lock=False),

    converters.PIPFileConverter(),
    converters.PIPFileLockConverter(),

    converters.PoetryConverter(),
    converters.PoetryLockConverter(),
])
def test_repository_preserve(converter):
    repo = RepositoriesRegistry()
    repo.add_repo(url='https://example.com', name='insane')
    repo.add_repo(url='https://pypi.org/simple/', name='pypi')
    root = RootDependency()
    dep1 = DependencyMaker.from_params(
        source=root,
        raw_name='dephell',
        constraint='*',
        repo=repo,
    )[0]
    req = Requirement(dep=dep1, roots=[root.name], lock=False)

    content1 = converter.dumps([req], project=root)
    root2 = converter.loads(content1)
    assert len(root2.dependencies) == 1
    dep2 = root2.dependencies[0]

    repos1 = [attr.asdict(repo) for repo in dep1.repo.repos]
    repos2 = [attr.asdict(repo) for repo in dep2.repo.repos]
    assert repos1 == repos2

# built-in
from pathlib import Path

# external
import pytest
from dephell_links import VCSLink

# project
from dephell.controllers import DependencyMaker
from dephell.converters import PIPFileConverter
from dephell.models import Requirement, RootDependency
from dephell.repositories import GitRepo


@pytest.mark.allow_hosts()
def test_load():
    converter = PIPFileConverter()
    root = converter.load(Path('tests') / 'requirements' / 'pipfile.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    assert 'requests' in deps
    assert 'records' in deps
    assert 'django' in deps
    assert 'nose' in deps
    assert str(deps['records'].constraint) == '>0.5.0'

    assert deps['django'].editable is True
    assert deps['requests'].editable is False

    assert deps['nose'].envs == {'dev'}
    assert deps['requests'].envs == {'main'}


@pytest.mark.allow_hosts()
def test_load_git_based_dep():
    converter = PIPFileConverter()
    root = converter.load(Path('tests') / 'requirements' / 'pipfile.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    dep = deps['django']
    assert isinstance(dep.link, VCSLink)
    assert isinstance(dep.repo, GitRepo)

    assert dep.link.vcs == 'git'
    assert dep.link.server == 'github.com'
    assert dep.link.name == 'django'


@pytest.mark.allow_hosts()
def test_dump():
    converter = PIPFileConverter()
    resolver = converter.load_resolver(Path('tests') / 'requirements' / 'pipfile.toml')
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2
    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'requests = ' in content
    assert "extras = ['socks']" in content
    assert 'records = ">0.5.0"' in content


def test_format_req():
    deps = DependencyMaker.from_params(
        raw_name='Django',
        constraint='>=1.9',
        source=RootDependency(),
    )
    content = PIPFileConverter()._format_req(Requirement(deps[0], lock=False))
    assert content == '>=1.9'


WAREHOUSE_TEST = """
[[source]]
url = 'https://pypi.python.org/simple'
verify_ssl = true
name = 'pypi'

[[source]]
url = 'https://myserver.org/'
verify_ssl = true
name = 'pypi3'

[packages]
pkg1 = {version='*', index='pypi'}
pkg3 = {version='*', index='pypi3'}
pkg4 = '*'
"""


@pytest.mark.allow_hosts()
def test_load_warehouse():
    converter = PIPFileConverter()
    root = converter.loads(WAREHOUSE_TEST)
    deps = {dep.name: dep for dep in root.dependencies}

    assert deps['pkg1'].repo.name == 'pypi'
    assert deps['pkg3'].repo.name == 'pypi3'
    assert deps['pkg4'].repo.name == 'pypi'

    assert deps['pkg1'].repo.url == 'https://pypi.org/pypi/', 'old url is not replaced'
    assert deps['pkg3'].repo.url == 'https://myserver.org/', 'server hostname is not used'
    assert deps['pkg4'].repo.url == 'https://pypi.org/pypi/', 'default url is not applied'

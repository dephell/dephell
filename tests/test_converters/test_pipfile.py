# project
from dephell.converters import PIPFileConverter
from dephell.links import VCSLink
from dephell.models import Dependency, Requirement, RootDependency
from dephell.repositories import GitRepo


def test_load():
    converter = PIPFileConverter()
    root = converter.load('./tests/requirements/pipfile.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    assert 'requests' in deps
    assert 'records' in deps
    assert 'django' in deps
    assert str(deps['records'].constraint) == '>0.5.0'

    assert deps['django'].editable is True
    assert deps['requests'].editable is False


def test_load_git_based_dep():
    converter = PIPFileConverter()
    root = converter.load('./tests/requirements/pipfile.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    dep = deps['django']
    assert isinstance(dep.link, VCSLink)
    assert isinstance(dep.repo, GitRepo)

    assert dep.link.vcs == 'git'
    assert dep.link.server == 'github.com'
    assert dep.link.name == 'django'


def test_dump():
    converter = PIPFileConverter()
    resolver = converter.load_resolver('./tests/requirements/pipfile.toml')
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2
    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'requests = ' in content
    assert "extras = ['socks']" in content
    assert 'records = ">0.5.0"' in content


def test_format_req():
    dep = Dependency.from_params(
        raw_name='Django',
        constraint='>=1.9',
        source=RootDependency(),
    )
    content = PIPFileConverter()._format_req(Requirement(dep, lock=False))
    assert content == '>=1.9'

from pathlib import Path

# project
from dephell.converters.poetry import PoetryConverter
from dephell.models import Requirement
from dephell.repositories.git.git import GitRepo


def test_load():
    converter = PoetryConverter()
    root = converter.load(Path('tests') / 'requirements' / 'poetry.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    assert 'requests' in deps
    assert 'toml' in deps

    assert set(deps['requests'].extras) == {'security'}
    assert deps['cleo'].link.rev == 'master'
    assert isinstance(deps['cleo'].repo, GitRepo)


def test_dump():
    converter = PoetryConverter()
    resolver = converter.load_resolver(Path('tests') / 'requirements' / 'poetry.toml')
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2
    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'requests = ' in content
    assert 'extras = ["security"]' in content
    assert 'pathlib2 = "==2.*,>=2.2.0"' in content

    assert 'https://github.com/sdispater/cleo.git' in content


# built-in
from pathlib import Path

# external
import tomlkit

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
    assert 'requests[security]' in deps

    assert deps['django'].link.rev == '1.11.4'
    assert isinstance(deps['django'].repo, GitRepo)


def test_dump():
    converter = PoetryConverter()
    resolver = converter.load_resolver(Path('tests') / 'requirements' / 'poetry.toml')
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2
    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'requests = ' in content
    assert 'extras = ["security"]' in content
    assert 'pathlib2 = "==2.*,>=2.2.0"' in content

    assert 'https://github.com/django/django.git' in content

    parsed = tomlkit.parse(content)['tool']['poetry']
    assert '>=0.9' in parsed['dependencies']['toml']
    assert '>=2.13' in parsed['dependencies']['requests']['version']
    assert {'security'} == set(parsed['dependencies']['requests']['extras'])

    assert parsed['dependencies']['django']['git'] == 'https://github.com/django/django.git'
    assert parsed['dependencies']['django']['rev'] == '1.11.4'

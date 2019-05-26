# built-in
from pathlib import Path

# external
import tomlkit

# project
from dephell.converters.poetry import PoetryConverter
from dephell.models import Requirement
from dephell.repositories import GitRepo


def test_load():
    converter = PoetryConverter()
    root = converter.load(Path('tests') / 'requirements' / 'poetry.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    assert 'requests' in deps
    assert 'toml' in deps
    assert 'requests[security]' in deps

    assert deps['django'].link.rev == '1.11.4'
    assert isinstance(deps['django'].repo, GitRepo)
    assert 'python_version >= "2.7.0"' in str(deps['pathlib2'].marker)

    assert deps['mysqlclient'].envs == {'main', 'mysql'}
    assert deps['pytest'].envs == {'dev'}


def test_dump():
    converter = PoetryConverter()
    resolver = converter.load_resolver(Path('tests') / 'requirements' / 'poetry.toml')
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2
    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'requests = ' in content
    assert 'extras = ["security"]' in content
    assert 'toml = "==0.*,>=0.9.0"' in content

    assert 'https://github.com/django/django.git' in content

    parsed = tomlkit.parse(content)['tool']['poetry']
    assert '>=0.9' in parsed['dependencies']['toml']
    assert '>=2.13' in parsed['dependencies']['requests']['version']
    assert {'security'} == set(parsed['dependencies']['requests']['extras'])

    assert parsed['dependencies']['pathlib2']['allows-prereleases'] is True
    assert parsed['dependencies']['pathlib2']['python'] == '==2.7.*,>=2.7.0'

    assert parsed['dependencies']['django']['git'] == 'https://github.com/django/django.git'
    assert parsed['dependencies']['django']['rev'] == '1.11.4'

    assert 'pytest' in parsed['dev-dependencies']


def test_entrypoints():
    converter = PoetryConverter()
    root = converter.load(Path('tests') / 'requirements' / 'poetry.toml')
    assert len(root.entrypoints) == 2

    content = converter.dumps(reqs=[], project=root)
    parsed = tomlkit.parse(content)['tool']['poetry']
    assert parsed['scripts']['my-script'] == 'my_package:main'
    assert dict(parsed['plugins']['flake8.extension']) == {'T00': 'flake8-todos.checker:Checker'}

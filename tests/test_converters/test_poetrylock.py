# built-in
from pathlib import Path

# external
import tomlkit

# project
from dephell.converters.poetrylock import PoetryLockConverter
from dephell.models import Requirement
from dephell.repositories import GitRepo


def test_load():
    converter = PoetryLockConverter()
    root = converter.load(Path('tests') / 'requirements' / 'poetry.lock.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    assert 'requests' in deps
    assert 'toml' in deps

    # assert str(deps['certifi'].group.best_release.version) == '2018.11.29'
    assert deps['django'].link.rev == '1.11.4'
    assert deps['django'].link.short == 'https://github.com/django/django.git'
    assert isinstance(deps['django'].repo, GitRepo)


def test_dump():
    converter = PoetryLockConverter()
    resolver = converter.load_resolver(Path('tests') / 'requirements' / 'poetry.lock.toml')
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2
    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'name = "enum34"' in content
    assert 'Python 3.4 Enum backported' in content

    parsed = tomlkit.parse(content)['package']
    parsed = {dep['name']: dep for dep in parsed}

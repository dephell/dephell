# built-in
from pathlib import Path

# project
from dephell.converters.poetrylock import PoetryLockConverter
from dephell.models import Requirement
from dephell.repositories.git.git import GitRepo


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

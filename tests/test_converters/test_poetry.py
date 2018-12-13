from pathlib import Path

# project
from dephell.converters.poetry import PoetryConverter


def test_load():
    converter = PoetryConverter()
    root = converter.load(Path('tests') / 'requirements' / 'poetry.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    assert 'requests' in deps
    assert 'toml' in deps

    assert set(deps['requests'].extras) == {'security'}

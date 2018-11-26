from pathlib import Path

# project
from dephell.converters.egginfo import EggInfoConverter


def test_load():
    path = Path('tests') / 'requirements' / 'sdist.tar.gz'
    root = EggInfoConverter().load(path)

    needed = {'attrs', 'cached-property', 'packaging', 'requests'}
    assert set(dep.name for dep in root.dependencies) == needed

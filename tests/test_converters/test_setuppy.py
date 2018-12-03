from pathlib import Path

# project
from dephell.converters.setuppy import SetupPyConverter


def test_load_deps():
    path = Path('tests') / 'requirements' / 'setup.py'
    root = SetupPyConverter().load(path)

    needed = {'attrs', 'cached-property', 'packaging', 'requests'}
    assert set(dep.name for dep in root.dependencies) == needed


def test_load_metadata():
    path = Path('tests') / 'requirements' / 'setup.py'
    root = SetupPyConverter().load(path)

    assert root.name == 'dephell'
    assert root.version == '0.2.0'
    assert root.authors[0].name == 'orsinium'
    assert not root.license

# built-in
from pathlib import Path

# project
from dephell.converters.wheel import WheelConverter


def test_load_deps():
    loader = WheelConverter()
    path = Path('tests') / 'requirements' / 'wheel.whl'
    root = loader.load(path)
    deps = {dep.name: dep for dep in root.dependencies}
    assert set(deps) == {'attrs', 'cached-property', 'packaging', 'requests'}


def test_load_metadata():
    loader = WheelConverter()
    path = Path('tests') / 'requirements' / 'wheel.whl'
    root = loader.load(path)

    assert root.name == 'dephell'
    assert root.version == '0.2.0'
    assert root.authors[0].name == 'orsinium'
    assert not root.license

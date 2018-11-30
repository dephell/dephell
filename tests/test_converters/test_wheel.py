from dephell.converters.wheel import WheelConverter
from pathlib import Path


def test_load():
    loader = WheelConverter()
    path = Path('tests') / 'requirements' / 'wheel.whl'
    root = loader.load(path)
    deps = {dep.name: dep for dep in root.dependencies}
    assert set(deps) == {'attrs', 'cached-property', 'packaging', 'requests'}

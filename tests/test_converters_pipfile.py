from dephell.converters.pipfile import PIPFileConverter


def test_load():
    loader = PIPFileConverter()
    root = loader.load('./tests/requirements/pipfile.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    assert 'requests' in deps
    assert 'records' in deps
    assert 'django' in deps
    assert str(deps['records'].constraint) == '>0.5.0'

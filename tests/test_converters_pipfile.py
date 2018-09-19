from dephell.converters.pipfile import PIPFileConverter


def test_load():
    converter = PIPFileConverter()
    root = converter.load('./tests/requirements/pipfile.toml')
    deps = {dep.name: dep for dep in root.dependencies}
    assert 'requests' in deps
    assert 'records' in deps
    assert 'django' in deps
    assert str(deps['records'].constraint) == '>0.5.0'


def test_dump():
    converter = PIPFileConverter()
    resolver = converter.load_resolver('./tests/requirements/pipfile.toml')
    for dep in resolver.graph.mapping['root'].dependencies:
        dep.__dict__['used'] = True
        resolver.graph.mapping[dep.name] = dep
    content = converter.dumps(resolver.graph)
    assert 'requests = ' in content
    assert "extras = ['socks']" in content
    assert 'records = ">0.5.0"' in content

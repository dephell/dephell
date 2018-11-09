# project
from dephell.converters import PIPFileConverter
from dephell.models import Requirement


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
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2
    content = converter.dumps(reqs=reqs)
    assert 'requests = ' in content
    assert "extras = ['socks']" in content
    assert 'records = ">0.5.0"' in content

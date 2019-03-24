# built-in
from pathlib import Path

# project
from dephell.converters.setuppy import SetupPyConverter
from dephell.models import Requirement


def test_load_deps():
    path = Path('tests') / 'requirements' / 'setup.py'
    root = SetupPyConverter().load(path)

    needed = {'attrs', 'cached-property', 'packaging', 'requests', 'colorama'}
    assert set(dep.name for dep in root.dependencies) == needed


def test_load_metadata():
    path = Path('tests') / 'requirements' / 'setup.py'
    root = SetupPyConverter().load(path)

    assert root.name == 'dephell'
    assert root.version == '0.2.0'
    assert root.authors[0].name == 'orsinium'
    assert not root.license


def test_dumps_deps():
    path = Path('tests') / 'requirements' / 'setup.py'
    converter = SetupPyConverter()
    resolver = converter.load_resolver(path)
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2

    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    print(content)
    root = SetupPyConverter().loads(content)
    needed = {'attrs', 'cached-property', 'packaging', 'requests', 'colorama'}
    assert set(dep.name for dep in root.dependencies) == needed

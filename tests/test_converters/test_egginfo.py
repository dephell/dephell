# built-in
from email.parser import Parser
from pathlib import Path

# project
from dephell.converters.egginfo import EggInfoConverter
from dephell.models import Requirement


def test_load_deps():
    path = Path('tests') / 'requirements' / 'sdist.tar.gz'
    root = EggInfoConverter().load(path)

    needed = {'attrs', 'cached-property', 'packaging', 'requests'}
    assert set(dep.name for dep in root.dependencies) == needed


def test_load_metadata():
    path = Path('tests') / 'requirements' / 'sdist.tar.gz'
    root = EggInfoConverter().load(path)

    assert root.name == 'dephell'
    assert root.version == '0.2.0'
    assert root.authors[0].name == 'orsinium'
    assert not root.license


def test_dumps_deps():
    path = Path('tests') / 'requirements' / 'sdist.tar.gz'
    converter = EggInfoConverter()
    resolver = converter.load_resolver(path)
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2

    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'Requires: requests' in content

    parsed = Parser().parsestr(content)
    needed = {'attrs', 'cached-property', 'packaging', 'requests'}
    assert set(parsed.get_all('Requires')) == needed


def test_dumps_metainfo():
    path = Path('tests') / 'requirements' / 'sdist.tar.gz'
    converter = EggInfoConverter()
    resolver = converter.load_resolver(path)
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2

    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'Requires: requests' in content

    parsed = Parser().parsestr(content)
    assert parsed.get('Name') == 'dephell'
    assert parsed.get('Version') == '0.2.0'
    assert parsed.get('Home-Page') == 'https://github.com/orsinium/dephell'

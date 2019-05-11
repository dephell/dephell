# built-in
from email.parser import Parser
from pathlib import Path

# project
from dephell.converters import EggInfoConverter
from dephell.models import Requirement


def test_load_deps():
    path = Path('tests') / 'requirements' / 'egg-info'
    root = EggInfoConverter().load(path)

    needed = {'attrs', 'cached-property', 'packaging', 'requests', 'colorama', 'libtest'}
    assert set(dep.name for dep in root.dependencies) == needed


def test_dumps_deps():
    path = Path('tests') / 'requirements' / 'egg-info'
    converter = EggInfoConverter()
    resolver = converter.load_resolver(path)
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2

    content = EggInfoConverter().dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'Requires-Dist: requests' in content

    parsed = Parser().parsestr(content)
    needed = {
        'attrs', 'cached-property', 'packaging', 'requests',
        'libtest', 'colorama; extra == "windows]"',
    }
    assert set(parsed.get_all('Requires-Dist')) == needed


def test_dumps_metainfo():
    path = Path('tests') / 'requirements' / 'egg-info'
    converter = EggInfoConverter()
    resolver = converter.load_resolver(path)
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2

    content = EggInfoConverter().dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'Requires-Dist: requests' in content

    parsed = Parser().parsestr(content)
    assert parsed.get('Name') == 'dephell'
    assert parsed.get('Version') == '0.2.0'
    assert parsed.get('Home-Page') == 'https://github.com/orsinium/dephell'

# built-in
from email.parser import Parser
from pathlib import Path

from dephell_links import VCSLink

# project
from dephell.converters import EggInfoConverter
from dephell.models import Requirement


def test_load_deps():
    path = Path('tests') / 'requirements' / 'egg-info'
    root = EggInfoConverter().load(path)

    needed = {'attrs', 'cached-property', 'packaging', 'requests', 'colorama', 'libtest'}
    assert {dep.name for dep in root.dependencies} == needed


def test_load_dependency_links():
    path = Path('tests') / 'requirements' / 'egg-info'
    root = EggInfoConverter().load(path)
    deps = {dep.name: dep for dep in root.dependencies}
    assert type(deps['libtest'].link) is VCSLink


def test_dump_dependency_links(temp_path):
    path = Path('tests') / 'requirements' / 'egg-info'
    temp_path /= 'test.egg-info'
    converter = EggInfoConverter()
    resolver = converter.load_resolver(path)
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    converter.dump(reqs=reqs, path=temp_path, project=resolver.graph.metainfo)

    content = (temp_path / 'dependency_links.txt').read_text()
    assert content.strip() == 'git+https://github.com/gwtwod/poetrylibtest#egg=libtest'


def test_dumps_deps():
    path = Path('tests') / 'requirements' / 'egg-info'
    converter = EggInfoConverter()
    resolver = converter.load_resolver(path)
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2

    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'Requires-Dist: requests' in content

    parsed = Parser().parsestr(content)
    needed = {
        'attrs', 'cached-property', 'packaging', 'requests',
        'libtest', 'colorama; extra == "windows"',
    }
    assert set(parsed.get_all('Requires-Dist')) == needed


def test_dumps_metainfo():
    path = Path('tests') / 'requirements' / 'egg-info'
    converter = EggInfoConverter()
    resolver = converter.load_resolver(path)
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2

    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    assert 'Requires-Dist: requests' in content

    parsed = Parser().parsestr(content)
    assert parsed.get('Name') == 'dephell'
    assert parsed.get('Version') == '0.2.0'
    assert parsed.get('Home-Page') == 'https://github.com/orsinium/dephell'

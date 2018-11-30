from pathlib import Path
from email.parser import Parser

# project
from dephell.converters.egginfo import EggInfoConverter
from dephell.models import Requirement


def test_load():
    path = Path('tests') / 'requirements' / 'sdist.tar.gz'
    root = EggInfoConverter().load(path)

    needed = {'attrs', 'cached-property', 'packaging', 'requests'}
    assert set(dep.name for dep in root.dependencies) == needed


def test_dumps():
    path = Path('tests') / 'requirements' / 'sdist.tar.gz'
    converter = EggInfoConverter()
    resolver = converter.load_resolver(path)
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2

    content = converter.dumps(reqs=reqs)
    assert 'Requires: requests' in content

    parsed = Parser().parsestr(content)
    needed = {'attrs', 'cached-property', 'packaging', 'requests'}
    assert set(parsed.get_all('Requires')) == needed

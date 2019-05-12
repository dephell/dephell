# built-in
from pathlib import Path

from dephell_links import VCSLink

# project
from dephell.converters.setuppy import SetupPyConverter
from dephell.models import Requirement


def test_load_deps():
    path = Path('tests') / 'requirements' / 'setup.py'
    root = SetupPyConverter().load(path)

    needed = {'attrs', 'cached-property', 'packaging', 'requests', 'colorama', 'libtest'}
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
    needed = {'attrs', 'cached-property', 'packaging', 'requests', 'colorama', 'libtest'}
    assert set(dep.name for dep in root.dependencies) == needed


def test_dependency_links_load():
    content = """
        __import__("setuptools").setup(
            name="lol",
            version="0.1.0",
            install_requires=["libtest"],
            dependency_links=["git+https://github.com/gwtwod/poetrylibtest#egg=libtest-0.1.0"],
        )
    """
    converter = SetupPyConverter()
    resolver = converter.loads_resolver(content.strip())
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    reqs = {req.name: req for req in reqs}
    assert type(reqs['libtest'].link) is VCSLink

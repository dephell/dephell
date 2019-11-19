# built-in
from pathlib import Path
from textwrap import dedent

# external
from dephell_links import VCSLink

# project
from dephell.converters.setuppy import SetupPyConverter
from dephell.models import Requirement


def test_load_deps():
    path = Path('tests') / 'requirements' / 'setup.py'
    root = SetupPyConverter().load(path)

    needed = {'attrs', 'cached-property', 'packaging', 'requests', 'colorama', 'libtest'}
    assert {dep.name for dep in root.dependencies} == needed


def test_load_metadata():
    path = Path('tests') / 'requirements' / 'setup.py'
    root = SetupPyConverter().load(path)

    assert root.name == 'dephell'
    assert root.version == '0.2.0'
    assert root.authors[0].name == 'orsinium'
    assert len(root.classifiers) == 4
    assert len(root.keywords) == 3
    assert not root.license


def test_dotted_setup_call(temp_path: Path):
    path = temp_path / 'setup.py'
    path.write_text(dedent("""
        import setuptools
        setuptools.setup(name='foo')
        """))
    root = SetupPyConverter().load(path)
    assert root.name == 'foo'


def test_return_setup_call(temp_path: Path):
    path = temp_path / 'setup.py'
    path.write_text(dedent("""
        from setuptools import setup
        def main():
            return setup(name='foo')

        if __name__ == '__main__':
            main()
        """))
    root = SetupPyConverter().load(path)
    assert root.name == 'foo'


def test_run_setup_function(temp_path: Path):
    path = temp_path / 'setup.py'
    path.write_text(dedent("""
        from setuptools import setup
        def run_setup():
            return setup(name='foo')

        if __name__ == '__main__':
            run_setup()
        """))
    root = SetupPyConverter().load(path)
    assert root.name == 'foo'


def test_import(temp_path: Path):
    path = temp_path / 'local_module.py'
    path.write_text(dedent('name = "imported"'))
    path = temp_path / 'setup.py'
    path.write_text(dedent("""
        from setuptools import setup
        import local_module
        setup(name=local_module.name)
        """))
    root = SetupPyConverter().load(path)
    assert root.name == 'imported'


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
    assert {dep.name for dep in root.dependencies} == needed


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

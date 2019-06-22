from pathlib import Path

from dephell_discover import Root as PackageRoot

from dephell.commands import ProjectVendorizeCommand
from dephell.controllers import DependencyMaker, Resolver, Graph, Mutator
from dephell.config import Config
from dephell.models import RootDependency


def test_extract_modules(temp_path: Path, requirements_dir: Path):
    config = Config()
    config.attach(dict(project=str(temp_path)))
    command = ProjectVendorizeCommand(argv=[], config=config)
    dep = DependencyMaker.from_requirement(source=RootDependency(), req='dephell')[0]
    result = command._extract_modules(
        dep=dep,
        archive_path=requirements_dir / 'wheel.whl',
        output_path=temp_path,
    )
    assert result is True
    assert (temp_path / 'dephell').exists()
    assert (temp_path / 'dephell' / '__init__.py').exists()


def test_patch_imports(temp_path: Path):
    (temp_path / 'project').mkdir()
    (temp_path / 'project' / '__init__.py').write_text('import requests\nimport django')
    (temp_path / 'project' / 'vendor' / 'requests').mkdir(parents=True)
    (temp_path / 'project' / 'vendor' / 'requests' / '__init__.py').touch()

    config = Config()
    config.attach(dict(project=str(temp_path)))
    package = PackageRoot(name='project', path=temp_path)
    root = RootDependency(raw_name='project', package=package)
    resolver = Resolver(
        graph=Graph(root),
        mutator=Mutator(),
    )
    command = ProjectVendorizeCommand(argv=[], config=config)
    command._patch_imports(
        resolver=resolver,
        output_path=temp_path / 'project' / 'vendor',
    )

    expected = 'import project.vendor.requests\nimport django'
    assert (temp_path / 'project' / '__init__.py').read_text() == expected

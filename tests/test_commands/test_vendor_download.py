from pathlib import Path

from dephell.commands import VendorDownloadCommand
from dephell.controllers import DependencyMaker
from dephell.config import Config
from dephell.models import RootDependency


def test_extract_modules(temp_path: Path, requirements_dir: Path):
    config = Config()
    config.attach(dict(project=str(temp_path)))
    command = VendorDownloadCommand(argv=[], config=config)
    dep = DependencyMaker.from_requirement(source=RootDependency(), req='dephell')[0]
    result = command._extract_modules(
        dep=dep,
        archive_path=requirements_dir / 'wheel.whl',
        output_path=temp_path,
    )
    assert result is True
    assert (temp_path / 'dephell').exists()
    assert (temp_path / 'dephell' / '__init__.py').exists()

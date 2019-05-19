# built-in
import shutil
from pathlib import Path

# project
from dephell.commands import ProjectBuildCommand
from dephell.config import Config


def test_build_command(temp_path: Path):
    metainfo_path = str(temp_path / 'pyproject.toml')
    shutil.copy(str(Path('tests') / 'requirements' / 'poetry.toml'), metainfo_path)
    config = Config()
    config.attach({
        'from': dict(format='poetry', path=metainfo_path),
        'project': str(temp_path),
    })
    command = ProjectBuildCommand(argv=[], config=config)
    result = command()
    assert result is True
    assert (temp_path / 'setup.py').exists()
    assert (temp_path / 'my_package.egg-info' / 'PKG-INFO').exists()
    assert (temp_path / 'dist' / 'my-package-0.1.0.tar.gz').exists()
    assert (temp_path / 'dist' / 'my_package-0.1.0-py3-none-any.whl').exists()

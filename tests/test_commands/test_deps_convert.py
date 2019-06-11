# built-in
import shutil
from pathlib import Path

# project
from dephell.commands import DepsConvertCommand
from dephell.config import Config


def test_convert_poetry_to_setup(temp_path: Path, requirements_dir: Path):
    from_path = str(temp_path / 'pyproject.toml')
    to_path = temp_path / 'setup.py'
    shutil.copy(str(requirements_dir / 'poetry.toml'), from_path)
    config = Config()
    config.attach({
        'from': dict(format='poetry', path=from_path),
        'to': dict(format='poetry', path=str(to_path)),
        'project': str(temp_path),
    })
    command = DepsConvertCommand(argv=[], config=config)
    result = command()
    assert result is True
    assert to_path.exists()
    content = to_path.read_text()
    assert 'The description of the package' in content


def test_convert_to_stdout(temp_path: Path, requirements_dir: Path, capsys):
    from_path = str(temp_path / 'pyproject.toml')
    shutil.copy(str(requirements_dir / 'poetry.toml'), from_path)
    config = Config()
    config.attach({
        'from': {'format': 'poetry', 'path': from_path},
        'to': {'format': 'setuppy', 'path': 'stdout'},
        'project': str(temp_path),
    })

    command = DepsConvertCommand(argv=[], config=config)
    result = command()

    assert result is True
    captured = capsys.readouterr()
    assert 'setup(' in captured.out
    assert 'The description of the package' in captured.out

# built-in
from pathlib import Path

# project
from dephell.commands import DepsConvertCommand
from dephell.config import Config


def test_convert_poetry_to_setup(temp_path: Path, requirements_path: Path):
    from_path = str(requirements_path / 'poetry.toml')
    to_path = temp_path / 'setup.py'
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


def test_convert_to_stdout(temp_path: Path, requirements_path: Path, capsys):
    from_path = str(requirements_path / 'poetry.toml')
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

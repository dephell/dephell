# built-in
import shutil
from pathlib import Path

# project
from dephell.commands import DepsConvertCommand
from dephell.config import Config


def test_convert_command(temp_path: Path):
    from_path = str(temp_path / 'pyproject.toml')
    to_path = temp_path / 'setup.py'
    shutil.copy(str(Path('tests') / 'requirements' / 'poetry.toml'), from_path)
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

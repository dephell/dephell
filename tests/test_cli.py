# built-in
from pathlib import Path

# external
import pytest

# project
from dephell.cli import get_command_name_and_size, main


@pytest.mark.parametrize('given, expected', [
    ('venv shell', 'venv shell'),
    ('shell venv', 'venv shell'),
    ('import', 'vendor import'),
    ('vnv shell', 'venv shell'),
    ('vnev shell', 'venv shell'),
    ('venv shll', 'venv shell'),
    ('venv shel', 'venv shell'),
    ('venv sl', None),
])
def test_get_command_name_and_size(given, expected):
    result = get_command_name_and_size(argv=given.split())
    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result[0] == expected


def test_main(temp_path: Path):
    config = temp_path / 'pyproject.toml'
    result = main(['generate config', '--config', str(config), '--project', str(temp_path)])
    assert result == 0

    assert config.exists()
    assert config.is_file()
    content = config.read_text()
    assert '[tool.dephell.example]' in content

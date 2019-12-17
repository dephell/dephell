# built-in
from pathlib import Path

# project
from dephell.cli import main


def test_main(temp_path: Path):
    config = temp_path / 'pyproject.toml'
    result = main(['generate', 'config', '--config', str(config), '--project', str(temp_path)])
    assert result == 0

    assert config.exists()
    assert config.is_file()
    content = config.read_text()
    assert '[tool.dephell.example]' in content

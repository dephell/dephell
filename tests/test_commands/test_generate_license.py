# built-in
from datetime import date
from pathlib import Path

# project
from dephell.commands import GenerateLicenseCommand
from dephell.config import Config


def test_generate_license_command(temp_path: Path):
    config = Config()
    config.attach({'project': str(temp_path)})
    command = GenerateLicenseCommand(argv=['MIT'], config=config)
    result = command()

    assert result is True
    assert (temp_path / 'LICENSE').exists()
    content = (temp_path / 'LICENSE').read_text()
    assert 'MIT License' in content
    assert str(date.today().year) in content

# built-in
from pathlib import Path

# project
from dephell.commands import GenerateEditorconfigCommand
from dephell.config import Config


def test_generate_editorconfig_command(temp_path: Path):
    (temp_path / 'setup.py').touch()
    (temp_path / 'README.md').touch()

    config = Config()
    config.attach({'project': str(temp_path)})
    command = GenerateEditorconfigCommand(argv=[], config=config)
    result = command()

    assert result is True
    assert (temp_path / '.editorconfig').exists()
    content = (temp_path / '.editorconfig').read_text()
    assert 'md' in content
    assert '[*.py]\nindent_style = space' in content
    assert 'Makefile' not in content
    assert '.go' not in content

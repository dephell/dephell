# built-in
from pathlib import Path

# external
from dephell_venvs import VEnv

# project
from dephell.commands import VenvCreateCommand
from dephell.config import Config


def test_venv_create_command(temp_path: Path):
    venv_path = temp_path / 'venv'
    venv = VEnv(path=venv_path)
    assert venv.exists() is False

    config = Config()
    config.attach({
        'project': str(temp_path),
        'venv': str(venv_path),
    })

    command = VenvCreateCommand(argv=[], config=config)
    result = command()

    assert result is True
    venv = VEnv(path=venv_path)
    assert venv.exists() is True

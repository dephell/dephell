# built-in
import sys
from pathlib import Path

# external
from dephell_venvs import VEnv

# project
from dephell.commands import VenvDestroyCommand
from dephell.config import Config


def test_venv_destroy_command(temp_path: Path):
    venv_path = temp_path / 'venv'
    venv = VEnv(path=venv_path)
    assert venv.exists() is False
    venv.create(python_path=sys.executable)

    config = Config()
    config.attach({
        'project': str(temp_path),
        'venv': str(venv_path),
    })

    command = VenvDestroyCommand(argv=[], config=config)
    result = command()

    assert result is True
    venv = VEnv(path=venv_path)
    assert venv.exists() is False

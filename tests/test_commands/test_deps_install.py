# built-in
import sys
from pathlib import Path

# external
import pytest
from dephell_venvs import VEnv

# project
from dephell.commands import DepsInstallCommand
from dephell.config import Config


@pytest.mark.allow_hosts()
def test_deps_install_command(temp_path: Path):
    reqs_path = temp_path / 'requirements.txt'
    reqs_path.write_text('six==1.12.0')

    venv_path = temp_path / 'venv'
    venv = VEnv(path=venv_path)
    assert venv.exists() is False
    venv.create(python_path=sys.executable)

    config = Config()
    config.attach({
        'from': dict(format='pip', path=str(reqs_path)),
        'project': str(temp_path),
        'venv': str(venv_path),
    })

    command = DepsInstallCommand(argv=[], config=config)
    result = command()

    assert result is True
    assert (venv.lib_path / 'six-1.12.0.dist-info' / 'METADATA').exists()

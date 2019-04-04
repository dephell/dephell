import sys
from pathlib import Path

from dephell.commands import DepsInstallCommand
from dephell.config import Config
from dephell.context_tools import env_var
from dephell.venvs import VEnv


def test_deps_install_command(temp_path: Path):
    reqs_path = temp_path / 'requirements.txt'
    reqs_path.write_text('six==1.12.0')

    venv_path = temp_path / 'venv'
    venv = VEnv(path=venv_path)
    venv.create(python_path=sys.executable)

    config = Config()
    config.attach({
        'to': dict(format='pip', path=str(reqs_path)),
        'project': str(temp_path),
        'venv': str(venv_path),
    })

    command = DepsInstallCommand(argv=[], config=config)
    with env_var('VIRTUAL_ENV', str(venv_path)):
        result = command()

    assert result is True
    assert (venv.lib_path / 'six-1.12.0.dist-info' / 'METADATA').exists()

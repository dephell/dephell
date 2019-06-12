# built-in
from pathlib import Path

# external
import pytest
from dephell_venvs import VEnv

# project
from dephell.commands import JailInstallCommand
from dephell.config import Config


@pytest.mark.allow_hosts()
def test_jail_install_command(temp_path: Path):
    venv_path = temp_path / 'venv'
    bin_path = temp_path / 'bin'
    bin_path.mkdir()

    config = Config()
    config.attach({
        'project': str(temp_path),
        'venv': str(venv_path),
        'bin': str(bin_path),
    })

    command = JailInstallCommand(argv=['pycodestyle==2.5.0'], config=config)
    result = command()

    assert result is True
    assert (bin_path / 'pycodestyle').exists()

    venv = VEnv(path=venv_path)
    assert venv.exists()
    assert (venv.bin_path / 'pycodestyle').exists()
    assert (venv.lib_path / 'pycodestyle-2.5.0.dist-info').exists()

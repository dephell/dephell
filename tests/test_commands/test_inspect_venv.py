# built-in
import json
import sys
from pathlib import Path

# external
from dephell_venvs import VEnv

# project
from dephell.commands import InspectVenvCommand
from dephell.config import Config


def test_inspect_venv_command(temp_path: Path, capsys):
    venv = VEnv(path=temp_path)
    venv.create(python_path=sys.executable)

    config = Config()
    config.attach({
        'project': str(temp_path),
        'venv': str(temp_path),
    })

    command = InspectVenvCommand(argv=[], config=config)
    result = command()
    assert result is True

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output['exists'] is True
    assert output['bin'] == str(venv.bin_path)

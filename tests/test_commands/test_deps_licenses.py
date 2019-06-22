# built-in
import json
from pathlib import Path

import pytest

# project
from dephell.commands import DepsLicensesCommand
from dephell.config import Config


@pytest.mark.allow_hosts()
def test_deps_licenses_command(temp_path: Path, capsys):
    reqs_path = temp_path / 'requirements.txt'
    reqs_path.write_text('six==1.12.0')

    config = Config()
    config.attach({
        'from': dict(format='pip', path=str(reqs_path)),
        'level': 'WARNING',
        'silent': True,
    })

    command = DepsLicensesCommand(argv=[], config=config)
    result = command()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert result is True
    assert output == {'MIT': ['six']}

# built-in
import json
import sys
from pathlib import Path

# external
import pytest
from dephell_venvs import VEnv

# project
from dephell.commands import DepsAuditCommand
from dephell.config import Config


@pytest.mark.allow_hosts()
def test_deps_audit_command(temp_path: Path, capsys):
    reqs_path = temp_path / 'requirements.txt'
    reqs_path.write_text('six==1.12.0')

    venv_path = temp_path / 'venv'
    venv = VEnv(path=venv_path)
    assert venv.exists() is False
    venv.create(python_path=sys.executable)

    config = Config()
    config.attach({
        'level': 'WARNING',
        'silent': True,
        'nocolors': True,
    })

    command = DepsAuditCommand(argv=['jinja2==2.0'], config=config)
    result = command()

    captured = capsys.readouterr()
    print(captured.err)
    print(captured.out)
    assert result is False
    output = json.loads(captured.out)
    assert len(output) >= 2
    for entry in output:
        assert entry['current'] == '2.0'
        assert entry['name'] == 'jinja2'

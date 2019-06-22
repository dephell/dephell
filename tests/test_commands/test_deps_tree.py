# built-in
import json
from pathlib import Path

# project
import pytest
from dephell.commands import DepsTreeCommand
from dephell.config import Config


@pytest.mark.allow_hosts()
def test_deps_tree_command(temp_path: Path, capsys):
    config = Config()
    config.attach({
        'level': 'WARNING',
        'silent': True,
    })

    command = DepsTreeCommand(argv=['--type=json', 'autopep8==1.4.3'], config=config)
    result = command()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert result is True
    assert len(output) == 2

    assert output[0]['name'] == 'autopep8'
    assert output[0]['dependencies'] == ['pycodestyle']

    assert output[1]['name'] == 'pycodestyle'
    assert output[1]['dependencies'] == []

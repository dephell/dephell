# built-in
import json
import sys
from pathlib import Path

# project
from dephell.commands import InspectProjectCommand
from dephell.config import Config


def test_inspect_project_command(temp_path: Path, capsys):
    config = Config()
    config.attach({
        'project': 'nani',
        'nocolors': True,
    })

    command = InspectProjectCommand(argv=[], config=config)
    result = command()
    assert result is True

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output['project_name']=='nani' 
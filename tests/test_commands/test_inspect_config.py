# built-in
import json
from pathlib import Path

# project
from dephell.commands import InspectConfigCommand
from dephell.config import Config


def test_inspect_config_command(temp_path: Path, capsys):
    config = Config()
    config.attach({
        'level': 'WARNING',
        'silent': True,
        'project': 'nani',
    })
    command = InspectConfigCommand(argv=[], config=config)
    result = command()
    assert result is True

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output['project'] == 'nani'
    assert output['level'] == 'WARNING'
    assert output['prereleases'] is False

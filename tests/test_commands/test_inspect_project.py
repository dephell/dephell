# built-in
import json
from pathlib import Path

# project
from dephell.commands import InspectProjectCommand
from dephell.config import Config


def test_inspect_project_command(temp_path: Path, requirements_path: Path, capsys):
    from_path = str(requirements_path / 'poetry.toml')
    config = Config()
    config.attach({
        'from': {'format': 'poetry', 'path': from_path},
        'to': {'format': 'setuppy', 'path': 'stdout'},
        'project': str(temp_path),
        'nocolors': True,
    })

    command = InspectProjectCommand(argv=[], config=config)
    result = command()
    assert result is True

    captured = capsys.readouterr()
    print(captured.out)
    output = json.loads(captured.out)
    assert output['project_name'] == 'my-package'

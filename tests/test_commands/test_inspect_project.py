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
        'project': str(temp_path),
        'nocolors': True,
        'silent': True,
    })

    command = InspectProjectCommand(argv=[], config=config)
    result = command()
    assert result is True

    captured = capsys.readouterr()
    print(captured.out)
    output = json.loads(captured.out)
    assert set(output) == {'name', 'version', 'description', 'links', 'python'}
    assert output['name'] == 'my-package'
    assert output['version'] == '0.1.0'

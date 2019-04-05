import json
from pathlib import Path

from dephell.commands import DepsOutdatedCommand
from dephell.config import Config


def test_deps_outdated_command(temp_path: Path, capsys):
    reqs_path = temp_path / 'requirements.txt'
    reqs_path.write_text('six==1.11.0')

    config = Config()
    config.attach({
        'to': dict(format='piplock', path=str(reqs_path)),
        'level': 'WARNING',
        'silent': True,
    })

    command = DepsOutdatedCommand(argv=[], config=config)
    result = command()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert result is True
    assert len(output) == 1
    assert output[0]['name'] == 'six'
    assert output[0]['installed'] == ['1.11.0']
    assert output[0]['latest'] != '1.11.0'

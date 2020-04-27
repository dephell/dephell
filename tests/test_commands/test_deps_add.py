# built-in
from pathlib import Path

# external
import pytest

# project
from dephell.commands import DepsAddCommand
from dephell.config import Config


@pytest.mark.allow_hosts()
def test_deps_add_command(temp_path: Path, capsys):
    reqs_path = temp_path / 'requirements.txt'
    reqs_path.write_text('six==1.12.0')

    config = Config()
    config.attach({
        'level': 'WARNING',
        'silent': True,
        'nocolors': True,
        'from': dict(format='pip', path=reqs_path),
    })

    command = DepsAddCommand(argv=['jinja2==2.0'], config=config)
    result = command()

    captured = capsys.readouterr()
    print(captured.err)
    print(captured.out)
    assert result is True

    assert set(reqs_path.read_text().split()) == {'six==1.12.0', 'jinja2==2.0'}

# built-in
from pathlib import Path


# project
from dephell.commands import ProjectBumpCommand
from dephell.config import Config


def test_bump_command(temp_path: Path):
    config = Config()
    config.attach({
        'project': str(temp_path),
    })
    command = ProjectBumpCommand(argv=[], config=config)
    result = command()
    assert result is True

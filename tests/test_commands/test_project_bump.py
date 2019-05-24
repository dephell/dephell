# built-in
from pathlib import Path


# project
from dephell.commands import ProjectBumpCommand
from dephell.config import Config


def test_bump_command(temp_path: Path):
    (temp_path / 'project').mkdir()
    init_path = (temp_path / 'project' / '__init__.py')
    init_path.write_text('__version__ = "1.2.3"')
    config = Config()
    config.attach({
        'project': str(temp_path),
    })
    command = ProjectBumpCommand(argv=['fix'], config=config)
    result = command()
    assert result is True
    assert init_path.read_text() == '__version__ = "1.2.4"'

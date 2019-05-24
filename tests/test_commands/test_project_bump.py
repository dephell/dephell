# built-in
from pathlib import Path


# project
from dephell.commands import ProjectBumpCommand
from dephell.config import Config
from dephell.actions import get_version_from_project
from dephell_discover import Root as PackageRoot


def test_bump_command(temp_path: Path):
    config = Config()
    config.attach({
        'project': str(temp_path),
    })
    package = PackageRoot(path=Path(config['project']))
    old_version = get_version_from_project(package)
    command = ProjectBumpCommand(argv=['serial'], config=config)
    result = command()
    new_version = get_version_from_project(package)
    assert result is True
    assert old_version != new_version

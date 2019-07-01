# built-in
from pathlib import Path

# third-party
import pytest

# project
from dephell.commands import ProjectBumpCommand
from dephell.config import Config
from dephell.actions._git import _run


def test_bump_command(temp_path: Path):
    project_path = (temp_path / 'project')
    project_path.mkdir()
    init_path = (project_path / '__init__.py')
    init_path.write_text('__version__ = "1.2.3"')
    config = Config()
    config.attach({
        'project': str(project_path),
    })
    command = ProjectBumpCommand(argv=['fix'], config=config)
    result = command()
    assert result is True
    assert init_path.read_text() == '__version__ = "1.2.4"'


@pytest.mark.parametrize('tag_template, expected_tag', [
    ('prefix.', 'prefix.1.2.4'),
    ('with.{version}.placeholder', 'with.1.2.4.placeholder'),
    ('', '1.2.4'),
    ('{version}', '1.2.4'),
])
def test_bump_command_with_placeholder_tag(temp_path: Path, tag_template, expected_tag):
    project_path = (temp_path / 'project')
    project_path.mkdir()
    init_path = (project_path / '__init__.py')
    init_path.write_text('__version__ = "1.2.3"')
    config = Config()
    config.attach({
        'project': str(project_path),
        'tag': tag_template,
    })
    # init local repo and add `__init__.py` to git index
    _run(['git', 'init'], project=project_path)

    # it's needed because bump command with tag generates not only tag, but also commit with --update flag
    # --update add to commit only modified files, not created (__init__.py in this case is created)
    _run(['git', 'add', '.'], project=project_path)

    command = ProjectBumpCommand(argv=['fix'], config=config)
    result = command()
    assert result is True

    # just read stdout from git tag command
    _, tags = _run(['git', 'tag'], project=project_path)
    assert tags == expected_tag

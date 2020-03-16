# built-in
from pathlib import Path

# project
from dephell.commands import ProjectRegisterCommand
from dephell.config import Config


def test_upd_pth(temp_path: Path):
    command = ProjectRegisterCommand(argv=[], config=Config())

    path = Path()
    command._upd_pth(lib_path=temp_path, project_path=path)
    content = (temp_path / 'dephell.pth').read_text()
    assert content == '{}\n'.format(path.absolute())

    another_path = Path(__file__)
    command._upd_pth(lib_path=temp_path, project_path=another_path)
    content = (temp_path / 'dephell.pth').read_text()
    assert content == '{}\n{}\n'.format(path.absolute(), another_path)


def test_upd_egg_link(temp_path: Path):
    command = ProjectRegisterCommand(argv=[], config=Config())
    lib_path = temp_path / 'lib'
    lib_path.mkdir()
    project_path = temp_path / 'project'
    project_path.mkdir()
    egg_info_path = project_path / 'project.egg-info'
    egg_info_path.mkdir()

    command._upd_egg_link(lib_path=lib_path, project_path=project_path)
    content = (lib_path / 'project.egg-link').read_text()
    assert content == '{}\n.'.format(egg_info_path.absolute())

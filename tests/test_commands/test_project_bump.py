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


def test_bump_pyproject(temp_path):
    import os
    import tomlkit

    os.chdir(str(temp_path))
    (temp_path / 'project').mkdir()
    from_path = temp_path / 'pyproject.toml'
    from_path.write_text("""
        [tool.dephell.main]
        from = {format="poetry", path="pyproject.toml"}
        versioning = "semver"

        [tool.poetry]
        version = "1.2.3"
        
        [[tool.poetry.source]]
        name = "pypi"
        url = "https://pypi.org/pypi"
    """)
    before_toml = tomlkit.loads(from_path.read_text())
    config = Config()
    config.attach_file(str(from_path), 'main')

    command = ProjectBumpCommand(argv=['fix'], config=config)
    result = command()

    assert result is True
    after_toml = tomlkit.loads(from_path.read_text())
    assert after_toml['tool']['poetry']['version'] == '1.2.4', 'Version was not bumped properly'
    after_toml['tool']['poetry']['version'] = '1.2.3'
    assert after_toml == before_toml, 'Bump command altered attributes other than version'


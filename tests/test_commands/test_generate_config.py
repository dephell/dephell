# built-in
from pathlib import Path

# external
import tomlkit

# project
from dephell.commands import GenerateConfigCommand


def test_create(temp_path: Path):
    config = temp_path / 'pyproject.toml'
    task = GenerateConfigCommand(['--config', str(config), '--project', str(temp_path)])
    result = task()
    assert result is True
    assert config.exists()
    assert config.is_file()
    content = config.read_text()
    parsed = tomlkit.parse(content)

    assert '[tool.dephell.example]' in content
    assert 'from = {format = "pip"' in content

    parsed = parsed['tool']['dephell']['example']
    assert parsed['from']['format'] == 'pip'
    assert parsed['from']['path'] == 'requirements.in'
    assert parsed['to']['format'] == 'piplock'
    assert parsed['to']['path'] == 'requirements.lock'


def test_detect(temp_path: Path):
    (temp_path / 'requirements.in').write_text('Django>=1.9\n')
    (temp_path / 'requirements.txt').write_text('Django>=1.9\n')

    config = temp_path / 'pyproject.toml'
    task = GenerateConfigCommand(['--config', str(config), '--project', str(temp_path)])
    result = task()
    assert result is True
    assert config.exists()
    assert config.is_file()
    content = config.read_text()
    parsed = tomlkit.parse(content)

    assert '[tool.dephell.pip]' in content
    assert 'from = {format = "pip"' in content

    parsed = parsed['tool']['dephell']['pip']
    assert parsed['from']['format'] == 'pip'
    assert parsed['from']['path'] == 'requirements.in'
    assert parsed['to']['format'] == 'piplock'
    assert parsed['to']['path'] == 'requirements.txt'

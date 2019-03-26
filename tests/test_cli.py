# project
from dephell.cli import main


def test_main(tmpdir):
    config = tmpdir.join('pyproject.toml')
    result = main(['generate config', '--config', str(config), '--project', str(tmpdir)])
    assert result == 0

    assert config.check(file=1, exists=1)
    content = config.read()
    assert '[tool.dephell.example]' in content

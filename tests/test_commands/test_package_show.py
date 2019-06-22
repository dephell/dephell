# built-in
import json

import pytest

# project
from dephell.commands import PackageShowCommand
from dephell.config import Config


@pytest.mark.allow_hosts()
def test_package_show_command(capsys):
    config = Config()
    config.attach({
        'level': 'WARNING',
        'silent': True,
    })

    command = PackageShowCommand(argv=['textdistance'], config=config)
    result = command()

    assert result is True
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output['name'] == 'textdistance'
    assert output['license'] == 'MIT'

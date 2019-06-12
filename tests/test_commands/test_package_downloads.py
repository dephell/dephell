# built-in
import json

import pytest

# project
from dephell.commands import PackageDownloadsCommand
from dephell.config import Config


@pytest.mark.allow_hosts()
def test_package_downloads_command(capsys):
    config = Config()
    config.attach({
        'level': 'WARNING',
        'silent': True,
    })

    command = PackageDownloadsCommand(argv=['DJANGO'], config=config)
    result = command()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert result is True
    assert len(output['pythons']) > 4
    assert len(output['systems']) > 2
    assert '█' in output['pythons'][0]['chart']

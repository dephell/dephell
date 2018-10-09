from dephell.config import Config


def test_load():
    config = Config.load('./tests/requirements/dephell.toml')
    section = config.get('some_env')
    assert section['from']['format'] == 'pip'

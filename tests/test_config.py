# built-in
from pathlib import Path

# external
import pytest

# project
from dephell.config import Config


def test_load():
    config = Config()
    config.attach_file(path=str(Path('tests') / 'requirements' / 'dephell.toml'), env='some_env')
    assert config['from']['format'] == 'pip'


@pytest.mark.parametrize('given, expected', [
    ({'DEPHELL_COMMAND': 'pip'}, {'command': 'pip'}),
    ({'DEPHELL_FROM_FORMAT': 'pip'}, {'from': {'format': 'pip'}}),
    ({'SOME_JUNK': 'pip'}, {}),
    ({'DEPHELL_ENV': 'pytest'}, {}),
    ({'DEPHELL_CACHE_TTL': '10'}, {'cache': {'ttl': 10}}),
    ({'DEPHELL_CACHE_TTL': '"10"'}, {'cache': {'ttl': '10'}}),
    ({'DEPHELL_TRACEBACK': 'true'}, {'traceback': True}),
    ({'DEPHELL_ENVS': '["main", "dev"]'}, {'envs': ['main', 'dev']}),
    (
        {'DEPHELL_FROM': '{format="pip", path="req.txt"}'},
        {'from': {'format': 'pip', 'path': 'req.txt'}},
    ),
])
def test_attach_env_vars(given, expected):
    config = Config()
    result = config.attach_env_vars(env_vars=given)
    assert result == expected

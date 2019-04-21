# project
from dephell.actions import make_travis


def test_make_travis_pytest(temp_path):
    config = {
        'some_env': {
            'from': {'format': 'setuppy', 'path': 'setup.py'},
            'command': 'pytest -x',
        },
        'bad_env': {
            'from': {'format': 'setuppy', 'path': 'setup.py'},
        },
    }
    content = make_travis(config=config)
    assert 'some_env' in content
    assert 'bad_env' not in content

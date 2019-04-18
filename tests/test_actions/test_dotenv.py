import pytest

from dephell.actions import read_dotenv


# https://github.com/jpadilla/django-dotenv/blob/master/tests.py
@pytest.mark.parametrize('lines, expected', [
    (['a=b # lol'], {'a': 'b'}),
    (['FOO=bar'], {'FOO': 'bar'}),
    (['FOO =bar'], {'FOO': 'bar'}),
    (['FOO= bar'], {'FOO': 'bar'}),
    (['FOO="bar"'], {'FOO': 'bar'}),
    (["FOO='bar'"], {'FOO': 'bar'}),  # noQA: Q0
    (['FOO="escaped\\"bar"'], {'FOO': 'escaped"bar'}),
    (['FOO='], {'FOO': ''}),
    (['FOO=test', 'BAR=$FOO'], {'FOO': 'test', 'BAR': 'test'}),
    (['FOO=test', 'BAR=${FOO}bar'], {'FOO': 'test', 'BAR': 'testbar'}),
])
def test_read_dotenv(temp_path, lines, expected):
    (temp_path / '.env').write_text('\n'.join(lines))
    assert read_dotenv(temp_path) == expected

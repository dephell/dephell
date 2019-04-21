# external
import pytest

# project
from dephell.actions import read_dotenv


# https://github.com/jpadilla/django-dotenv/blob/master/tests.py
# https://github.com/motdotla/dotenv/blob/master/tests/.env
@pytest.mark.parametrize('lines, expected', [
    (['a=b # lol'], {'a': 'b'}),

    # strip spaces
    (['FOO=bar'], {'FOO': 'bar'}),
    (['FOO =bar'], {'FOO': 'bar'}),
    (['FOO= bar'], {'FOO': 'bar'}),
    (['FOO=bar  '], {'FOO': 'bar'}),
    (['  FOO=bar'], {'FOO': 'bar'}),
    (['take =   me out  '], {'take': 'me out'}),

    # quotes
    (['FOO="bar"'], {'FOO': 'bar'}),
    (["FOO='bar'"], {'FOO': 'bar'}),

    # key formats
    (['FOO.BAR=foobar'], {'FOO.BAR': 'foobar'}),

    # empty
    (['FOO='], {'FOO': ''}),
    (['FOO=   '], {'FOO': ''}),

    # substitution
    (['FOO=test', 'BAR=$FOO'], {'FOO': 'test', 'BAR': 'test'}),
    (['FOO=test', 'BAR=${FOO}bar'], {'FOO': 'test', 'BAR': 'testbar'}),

    # escaping
    ([r'FOO="escaped\"bar"'], {'FOO': 'escaped"bar'}),
    (['FOO=test', r'BAR="foo\$FOO"'], {'FOO': 'test', 'BAR': 'foo$FOO'}),
    (['FOO=test', r'BAR="foo\${FOO}"'], {'FOO': 'test', 'BAR': 'foo${FOO}'}),

    # escape sequences
    ([r'take="me\nout"'], {'take': 'me\nout'}),
    ([r'take="me\out"'], {'take': r'me\out'}),

    # comments
    (['take=me # out'], {'take': 'me'}),
    (['take="me # to" # church'], {'take': 'me # to'}),
    (['take="me" # to # church'], {'take': 'me'}),
    (['take="me # out"'], {'take': 'me # out'}),
    (['# take', 'me=out'], {'me': 'out'}),
])
def test_read_dotenv(temp_path, lines, expected):
    (temp_path / '.env').write_text('\n'.join(lines))
    assert read_dotenv(temp_path) == expected

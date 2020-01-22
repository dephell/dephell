import pytest

from dephell.actions._changelog import _get_version


@pytest.mark.parametrize('given, expected', [
    ('Version 1.1.2',               '1.1.2'),   # flask
    ('## v.0.8.0 (2019-12-19)',     '0.8.0'),   # dephell
    ('0.14.0 (2018-01-9)',          '0.14.0'),  # changelogs
    ('Mayavi 4.5.0',                '4.5.0'),   # mayavi
    ('v0.16.0',                     '0.16.0'),  # py-trello
    ('1.11.7',                      '1.11.7'),  # boto3
    ('2.2.2 (2019-12-26)',          '2.2.2'),   # dynaconf
    ('20.0.1 (2020-01-21)',         '20.0.1'),  # pip
    ('* :release:`1.11.0 <2018-03-19>`', '1.11.0'),   # twine
    ("What's new in psycopg 2.8.4", '2.8.4'),   # psycopg2-binary
])
def test_get_version(given: str, expected: str):
    assert _get_version(given) == expected

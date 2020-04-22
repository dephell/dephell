# external
import pytest

# project
from dephell.commands import PackageBugCommand


@pytest.mark.parametrize('links, url', [
    (
        {'home': 'https://bitbucket.org/saaj/torrelque'},
        'https://bitbucket.org/saaj/torrelque/issues/new',
    ),
    (
        {'repository': 'https://github.com/dephell/dephell'},
        'https://github.com/dephell/dephell/issues/new',
    ),
    (
        {'home': 'https://gitlab.com/pycqa/flake8'},
        'https://gitlab.com/pycqa/flake8/issues/new',
    ),
    (
        {'Tracker': 'https://code.djangoproject.com/'},
        'https://code.djangoproject.com/',
    ),
])
def test_get_url(requests_mock, links, url):
    requests_mock.head(url)
    assert PackageBugCommand._get_url(links=links) == url



# project
import pytest
from dephell.links import DirLink, FileLink, URLLink, VCSLink, parse_link


@pytest.mark.parametrize('link_type, url', [
    (VCSLink, 'https://github.com/r1chardj0n3s/parse.git'),
    (URLLink, 'https://github.com/divio/django-cms/archive/release/3.4.x.zip'),
    (FileLink, './tests/requirements/setup.py'),
    (DirLink, '.'),
])
def test_parsing(link_type, url):
    link = parse_link(url)
    assert isinstance(link, link_type)
    assert link.short == url

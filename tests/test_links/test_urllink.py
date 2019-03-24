

# project
import pytest
from dephell.links import URLLink


@pytest.mark.parametrize('url, name', [
    ('https://github.com/divio/django-cms/archive/release/3.4.x.zip', 'django-cms'),
    ('https://github.com/pypa/pip/archive/1.3.1.zip#sha1=da9234ee9982d4bbb3c72346a6de940a148ea686', 'pip'),
    ('https://github.com/orsinium/textdistance/archive/master.zip', 'textdistance'),
    ('https://files.pythonhosted.org/packages/00/a0/blabla/textdistance-4.1.2.tar.gz', 'textdistance'),
])
def test_name(url, name):
    link = URLLink(url)
    assert link.name == name

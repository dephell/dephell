import pytest
from dephell.repositories.warehouse._simple import SimpleWareHouseRepo


@pytest.mark.parametrize('fname, name, version', [
    ('dephell-0.7.3-py3-none-any.whl', 'dephell', '0.7.3'),
    ('dephell-0.7.3.tar.gz', 'dephell', '0.7.3'),

    ('flake8_commas-2.0.0-py2.py3-none-any.whl', 'flake8_commas', '2.0.0'),
    ('flake8-commas-2.0.0.tar.gz ', 'flake8-commas', '2.0.0'),
])
def test_parse_name(fname, name, version):
    assert SimpleWareHouseRepo._parse_name(fname) == (name, version)

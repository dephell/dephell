import pytest

from dephell.converters import ImportsConverter


@pytest.mark.parametrize('lines, expected', [
    (['from django import forms'], {'Django'}),
])
def test_imports_parser(lines, expected):
    converter = ImportsConverter()
    modules = converter._get_modules(content='\n'.join(lines))
    assert modules == expected

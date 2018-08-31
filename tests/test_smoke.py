import pytest

from dephell.core import Resolver


def test_one():
    resolver = Resolver.from_requirements('./tests/requirements/1.txt')
    resolver.resolve()
    assert 'Django' in resolver.graph


def test_two_different():
    resolver = Resolver.from_requirements('./tests/requirements/2.txt')
    resolver.resolve()
    assert 'Django' in resolver.graph
    assert 'deal' in resolver.graph


def test_unresolved():
    resolver = Resolver.from_requirements('./tests/requirements/3.txt')
    with pytest.raises(ImportError):
        resolver.resolve()

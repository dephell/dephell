# project
import pytest
from dephell.resolver import Resolver


def test_one():
    resolver = Resolver.from_requirements('./tests/requirements/django.txt')
    resolver.resolve()
    assert 'Django' in resolver.graph


def test_two_different():
    resolver = Resolver.from_requirements('./tests/requirements/django-deal.txt')
    resolver.resolve()
    assert 'Django' in resolver.graph
    assert 'deal' in resolver.graph


def test_unresolved():
    resolver = Resolver.from_requirements('./tests/requirements/django-django.txt')
    with pytest.raises(ImportError):
        resolver.resolve()


def test_resolution():
    resolver = Resolver.from_requirements('./tests/requirements/scipy-pandas-numpy.txt')
    resolver.resolve()
    assert 'pandas' in resolver.graph
    assert 'scipy' in resolver.graph
    assert 'numpy' in resolver.graph

    assert resolver.graph['numpy'].best_release.version == '1.15.1'
    assert resolver.graph['scipy'].best_release.version == '0.19.1'
    assert resolver.graph['pandas'].best_release.version > '0.20.3'


def test_unlocked():
    resolver = Resolver.from_requirements('./tests/requirements/attrs-requests.txt')
    resolver.resolve()
    assert 'attrs' in resolver.graph
    assert 'requests' in resolver.graph

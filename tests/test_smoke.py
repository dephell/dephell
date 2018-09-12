# project
import pytest
from dephell3.constructors import from_requirements


def test_one():
    resolver = from_requirements('./tests/requirements/django.txt')
    resolved = resolver.resolve()
    assert resolved is True
    assert 'django' in resolver.graph.mapping


def test_two_different():
    resolver = from_requirements('./tests/requirements/django-deal.txt')
    resolved = resolver.resolve()
    assert resolved is True
    assert 'django' in resolver.graph.mapping.keys()
    assert 'deal' in resolver.graph.mapping.keys()


# def test_unresolved():
#     resolver = Resolver.from_requirements('./tests/requirements/django-django.txt')
#     with pytest.raises(ImportError):
#         resolver.resolve()
#
#
# def test_resolution():
#     resolver = Resolver.from_requirements('./tests/requirements/scipy-pandas-numpy.txt')
#     resolver.resolve()
#     assert 'pandas' in resolver.graph
#     assert 'scipy' in resolver.graph
#     assert 'numpy' in resolver.graph
#
#     assert resolver.graph['numpy'].best_release.version == '1.15.1'
#     assert resolver.graph['scipy'].best_release.version == '0.19.1'
#     assert resolver.graph['pandas'].best_release.version > '0.20.3'
#
#
# def test_unlocked():
#     resolver = Resolver.from_requirements('./tests/requirements/attrs-requests.txt')
#     resolver.resolve()
#     assert 'attrs' in resolver.graph
#     assert 'requests' in resolver.graph
#
#
# def test_subpackages():
#     resolver = Resolver.from_requirements('./tests/requirements/oslo.txt')
#     resolver.resolve()
#     assert 'oslo.utils' in resolver.graph

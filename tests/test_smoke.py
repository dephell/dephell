from dephell.core import Resolver


def test_one():
    resolver = Resolver.from_requirements('./tests/requirements/1.txt')
    resolver.resolve()
    assert 'Django' in resolver.graph

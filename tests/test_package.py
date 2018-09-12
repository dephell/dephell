# external
from packaging.requirements import Requirement

# project
from dephell3.models import Dependency, RootDependency


def test_from_requirement():
    root = RootDependency([])
    req = Requirement('Django>=1.5,<=1.9')
    p = Dependency.from_requirement(source=root, req=req)
    assert p.name == 'Django'
    assert set(str(p.constraint).split(',')) == {'>=1.5', '<=1.9'}



# external
from packaging.requirements import Requirement

# project
from dephell.controllers import DependencyMaker
from dephell.models import RootDependency


def test_from_requirement():
    root = RootDependency()
    req = Requirement('Django>=1.5,<=1.9')
    p = DependencyMaker.from_requirement(source=root, req=req)[0]
    assert p.raw_name == 'Django'
    assert set(str(p.constraint).split(',')) == {'>=1.5', '<=1.9'}

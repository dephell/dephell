# external
from packaging.requirements import Requirement

# project
from dephell.package import Package


def test_from_requirement():
    req = Requirement('Django>=1.5,<=1.9')
    p = Package.from_requirement(req)
    assert p.name == 'Django'
    assert set(p.version_spec.split(',')) == {'>=1.5', '<=1.9'}

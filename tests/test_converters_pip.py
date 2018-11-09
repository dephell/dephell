# external
from packaging.requirements import Requirement as PackagingRequirement

# project
from dephell.converters.pip import PIPConverter
from dephell.models import Dependency, Requirement, RootDependency


def test_format():
    root = RootDependency()
    text = (
        'hypothesis[django]<=3.0.0; '
        'python_version == "2.7" and '
        'platform_python_implementation == "CPython"'
    )
    req = PackagingRequirement(text)
    dep = Dependency.from_requirement(root, req)

    # test dep
    assert dep.name == 'hypothesis'
    assert dep.extras == {'django', }
    assert str(dep.constraint) == '<=3.0.0'
    assert str(dep.marker).startswith('python_version == "2.7"')

    # test format
    result = PIPConverter(lock=False)._format_req(
        req=Requirement(dep=dep, lock=False),
    )
    assert 'hypothesis[django]' in result
    assert '<=3.0.0' in result
    assert 'python_version == "2.7"' in result
    assert 'from root' in result
    assert result.startswith(text)

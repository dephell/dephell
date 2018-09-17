from dephell.converters.pip import _format_dep
from packaging.requirements import Requirement
from dephell.models.dependency import Dependency
from dephell.models.root import RootDependency


def test_format():
    root = RootDependency()
    text = (
        'hypothesis[django]<=3.0.0; '
        'python_version == "2.7" and '
        'platform_python_implementation == "CPython"'
    )
    req = Requirement(text)
    dep = Dependency.from_requirement(root, req)

    # test dep
    assert dep.name == 'hypothesis'
    assert dep.extras == {'django', }
    assert str(dep.constraint) == '<=3.0.0'
    assert str(dep.marker).startswith('python_version == "2.7"')

    # test format
    result = _format_dep(dep, lock=False)
    assert result.startswith(text)
    assert 'from root' in result

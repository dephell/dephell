# external
from dephell_links import VCSLink
from packaging.requirements import Requirement as PackagingRequirement

# project
from dephell.controllers import DependencyMaker
from dephell.converters.pip import PIPConverter
from dephell.models import Requirement, RootDependency
from dephell.repositories import GitRepo


def test_format():
    root = RootDependency()
    text = (
        'hypothesis[django]<=3.0.0; '
        'python_version == "2.7" and '
        'platform_python_implementation == "CPython"'
    )
    req = PackagingRequirement(text)
    deps = DependencyMaker.from_requirement(root, req)

    # test dep
    assert deps[0].name == 'hypothesis'
    assert deps[1].name == 'hypothesis[django]'
    assert str(deps[0].constraint) == '<=3.0.0'
    assert str(deps[0].marker).startswith('python_version == "2.7"')

    # test format
    req = Requirement(dep=deps[0], lock=False)
    req.extra_deps = (deps[1], )
    result = PIPConverter(lock=False)._format_req(req=req)
    assert 'hypothesis[django]' in result
    assert '<=3.0.0' in result
    assert 'python_version == "2.7"' in result
    assert 'from root' not in result
    assert result.startswith(text)


def test_git_parsing():
    root = PIPConverter(lock=False).loads('-e git+https://github.com/django/django.git#egg=django')
    assert len(root.dependencies) == 1
    dep = root.dependencies[0]

    assert isinstance(dep.link, VCSLink)
    assert isinstance(dep.repo, GitRepo)

    assert dep.link.vcs == 'git'
    assert dep.link.server == 'github.com'
    assert dep.link.name == 'django'

    assert dep.name == 'django'
    assert dep.editable is True

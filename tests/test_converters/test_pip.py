# built-in
from pathlib import Path

# external
import pytest
from dephell_links import VCSLink
from packaging.requirements import Requirement as PackagingRequirement

# project
from dephell.controllers import DependencyMaker
from dephell.converters.pip import PIPConverter
from dephell.models import Requirement, RootDependency
from dephell.repositories import GitRepo


@pytest.mark.parametrize('lock, given, expected', [
    # only non-lock can parse classic name
    (False, ['requirements.txt'], ['requirements.txt']),
    (True, ['requirements.txt'], []),

    # same for non-classic name
    (False, ['requirements-test.txt'], ['requirements-test.txt']),
    (True, ['requirements-test.txt'], []),

    # in pair lock+in every parser takes only its file
    (False, ['requirements.in', 'requirements.lock'], ['requirements.in']),
    (True, ['requirements.in', 'requirements.lock'], ['requirements.lock']),

    # correct matching for in+txt and txt+lock pairs
    (False, ['requirements.in', 'requirements.txt'], ['requirements.in']),
    (True, ['requirements.in', 'requirements.txt'], ['requirements.txt']),
    (False, ['requirements.txt', 'requirements.lock'], ['requirements.txt']),
    (True, ['requirements.txt', 'requirements.lock'], ['requirements.lock']),

    # don't match invalid names
    (True, ['req.txt'], []),
    (False, ['req.txt'], []),
])
def test_can_parse(temp_path: Path, lock: bool, given: list, expected: list):
    for name in given:
        (temp_path / name).touch()
    for name in given:
        actual = PIPConverter(lock=lock).can_parse(path=(temp_path / name))
        assert actual is (name in expected)


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


@pytest.mark.parametrize('path, expected', [
    ('-e git+https://github.com/django/django.git#egg=django', None),
    ('./project', None),
])
def test_preserve_path(temp_path: Path, path: str, expected: str):
    (temp_path / 'project').mkdir()
    (temp_path / 'project' / 'setup.py').touch()
    req_path = (temp_path / 'requirements.txt')
    req_path.write_text(path)

    converter = PIPConverter(lock=False).copy(project_path=temp_path)
    root = converter.load(req_path)
    req = Requirement(dep=root.dependencies[0], lock=False)
    dumped = converter.dumps(reqs=[req], project=root)
    if expected is None:
        expected = path
    assert dumped.strip() == expected

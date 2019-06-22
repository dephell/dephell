from os import environ

import pytest

# project
from dephell.controllers import DependencyMaker
from dephell.models import RootDependency
from dephell.repositories import CondaRepo, CondaGitRepo, CondaCloudRepo


@pytest.mark.allow_hosts()
@pytest.mark.parametrize('repo_class', [CondaRepo, CondaCloudRepo])
def test_conda_get_releases(repo_class):
    repo = repo_class(channels=['conda-forge'])
    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='textdistance')[0]
    releases = repo.get_releases(dep=dep)
    versions = {str(release.version) for release in releases}
    assert not {'3.0.3', '3.1.0', '4.0.0', '4.1.0'} - versions


@pytest.mark.allow_hosts()
@pytest.mark.skipif('TRAVIS_OS_NAME' in environ, reason='Travis CI usually out of rate for Github')
def test_conda_get_releases_git():
    repo = CondaGitRepo(channels=['conda-forge'])
    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='textdistance')[0]
    releases = repo.get_releases(dep=dep)
    versions = {str(release.version) for release in releases}
    assert not {'3.0.3', '3.1.0', '4.0.0', '4.1.0'} - versions


@pytest.mark.allow_hosts()
@pytest.mark.parametrize('repo_class', [CondaRepo, CondaCloudRepo])
def test_conda_deps(repo_class):
    repo = repo_class(channels=['bioconda'])
    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='anvio')[0]
    releases = repo.get_releases(dep=dep)
    deps = {dep.name for dep in releases[0].dependencies}
    assert 'prodigal' in deps


@pytest.mark.allow_hosts()
@pytest.mark.skipif('TRAVIS_OS_NAME' in environ, reason='Travis CI usually out of rate for Github')
def test_conda_deps_git():
    repo = CondaGitRepo(channels=['bioconda'])
    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='anvio')[0]
    releases = repo.get_releases(dep=dep)
    deps = {dep.name for dep in releases[0].dependencies}
    assert 'prodigal' in deps

# built-in
import json
from pathlib import Path

# external
import pytest
from dephell_links import VCSLink

# project
from dephell.converters import PIPFileLockConverter
from dephell.models import Requirement
from dephell.repositories import GitRepo


@pytest.mark.allow_hosts()
def test_load():
    converter = PIPFileLockConverter()
    # https://github.com/pypa/pipfile/blob/master/examples/Pipfile.lock
    root = converter.load(Path('tests') / 'requirements' / 'pipfile.lock.json')
    deps = {dep.name: dep for dep in root.dependencies}
    assert 'requests' in deps
    assert 'records' in deps
    assert 'django' in deps
    assert str(deps['records'].constraint) == '==0.5.2'
    assert len(deps['pyyaml'].group.best_release.hashes) == 14


@pytest.mark.allow_hosts()
def test_load_git_based_dep():
    converter = PIPFileLockConverter()
    root = converter.load(Path('tests') / 'requirements' / 'pipfile.lock.json')
    deps = {dep.name: dep for dep in root.dependencies}
    dep = deps['django']
    assert isinstance(dep.link, VCSLink)
    assert isinstance(dep.repo, GitRepo)

    assert dep.link.vcs == 'git'
    assert dep.link.server == 'github.com'
    assert dep.link.name == 'django'


@pytest.mark.allow_hosts()
def test_dump():
    converter = PIPFileLockConverter()
    resolver = converter.load_resolver(Path('tests') / 'requirements' / 'pipfile.lock.json')
    reqs = Requirement.from_graph(graph=resolver.graph, lock=False)
    assert len(reqs) > 2
    content = converter.dumps(reqs=reqs, project=resolver.graph.metainfo)
    content = json.loads(content)
    assert content['default']['chardet']['version'] == '==3.0.4'

    assert 'nose' not in content['default']
    assert 'nose' in content['develop']

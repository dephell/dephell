# built-in
import asyncio
from pathlib import Path

# project
from dephell.repositories.git.git import GitRepo
from dephell_links import VCSLink


loop = asyncio.get_event_loop()


class PatchedVCSLink(VCSLink):
    short = str(Path('.').resolve())


class Dep:
    raw_name = 'DepHell'


def test_releases():
    link = PatchedVCSLink(server=None, author=None, project=None, name='dephell')
    repo = GitRepo(link)

    releases = repo.get_releases(Dep)
    assert len(releases) >= 1
    assert len(releases) == len(repo.tags)

    assert releases[0].name == 'dephell'
    assert str(releases[0].version) == '0.1.0'
    assert str(releases[1].version) == '0.1.5'


def test_deps():
    link = PatchedVCSLink(server=None, author=None, project=None, name='dephell')
    repo = GitRepo(link)

    coroutine = repo.get_dependencies('dephell', '0.1.0')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    assert len(deps) == 4
    assert set(dep.name for dep in deps) == {'attrs', 'cached-property', 'packaging', 'requests'}


def test_metaversion():
    link = PatchedVCSLink(server=None, author=None, project=None, name='dephell')
    repo = GitRepo(link)

    rev = 'abce8710f335bba0977745a137a06ce59f2bfbde'
    assert repo.get_nearest_version(rev) == '0.1.0'

    rev = '29c9eb3a9fd9e87ee7c24ac5eca9bc6d4b9a627a'
    assert repo.get_nearest_version(rev) == '0.1.5'

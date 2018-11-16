from pathlib import Path
import asyncio

from dephell.repositories.git.git import GitRepo
from dephell.links import VCSLink


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
    assert len(repo.commits) > len(repo.tags)

    first_release = releases[0]
    assert first_release.name == 'dephell'
    assert str(first_release.version) == '0.1.0'


def test_deps():
    link = PatchedVCSLink(server=None, author=None, project=None, name='dephell')
    link.short = '.'
    repo = GitRepo(link)

    coroutine = repo.get_dependencies('dephell', '0.1.0')
    deps = loop.run_until_complete(asyncio.gather(coroutine))[0]
    assert len(deps) == 4
    assert set(dep.name for dep in deps) == {'attrs', 'cached-property', 'packaging', 'requests'}

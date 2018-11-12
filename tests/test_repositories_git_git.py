from dephell.repositories.git.git import GitRepo
from dephell.links import VCSLink


class PatchedVCSLink(VCSLink):
    short = '.'


class Dep:
    raw_name = 'DepHell'


def test_releases():
    link = PatchedVCSLink(server=None, author=None, project=None, name='dephell')
    link.short = '.'
    repo = GitRepo(link)

    releases = repo.get_releases(Dep)
    assert len(releases) >= 1
    assert len(releases) == len(repo._get_tags())
    assert len(repo._get_commits()) > len(repo._get_tags())

    first_release = releases[0]
    assert first_release.name == 'dephell'
    assert str(first_release.version) == '0.1.0'

from collections import OrderedDict
from datetime import datetime

from dephell.repositories.git.git import GitRepo
from dephell.links import VCSLink
from dephell.models import Dependency, RootDependency


class PatchedGitRepo(GitRepo):
    commits = OrderedDict([
        ('11bcb57ee2064d795f5f596eade244168ef5ed65', datetime(2018, 7, 30, 15, 41)),
        ('9cac10eee49eae3bbf7bd133ba0ae931b275324c', datetime(2018, 7, 29, 15, 41)),
        ('e62f6e0968eb19a44198211b5398c5738db454c5', datetime(2018, 7, 28, 15, 41)),  # 1.11
        ('0cf85e6b074794ac91857aa097f0b3dc3e6d9468', datetime(2018, 7, 27, 15, 41)),
        ('f436c82637dafa3a9abbd65a3be77bf7ad431213', datetime(2018, 7, 26, 15, 41)),  # 1.9
        ('2fd21a18584dc62cfad65cc112465ce68db5561a', datetime(2018, 7, 25, 15, 41)),
        ('ec16588c27f7ea80d5ee3d5b19331ef9216e2530', datetime(2018, 7, 25, 15, 41)),  # 1.7
        ('405ec5b9c6996bf4e5fba68a9bad76d17e146327', datetime(2018, 7, 25, 15, 41)),
    ])
    tags = OrderedDict([
        ('e62f6e0968eb19a44198211b5398c5738db454c5', 'refs/tags/v1.11'),
        ('f436c82637dafa3a9abbd65a3be77bf7ad431213', 'refs/tags/v.1.9'),
        ('ec16588c27f7ea80d5ee3d5b19331ef9216e2530', 'refs/tags/1.7'),
    ])

    def _setup(self):
        raise Exception('called _setup in PatchedGitRepo')

    async def get_dependencies(self, name: str, version: str) -> tuple:
        return tuple()


def test_no_rev_one_constraint():
    dep = Dependency.from_params(
        raw_name='Django',
        constraint='',
        source=RootDependency(),
        url='https://github.com/django/django.git',
    )
    assert isinstance(dep.link, VCSLink)
    assert isinstance(dep.repo, GitRepo)
    dep.repo = PatchedGitRepo(dep.link)

    releases = set()
    for group in dep.groups:
        assert not group.empty
        releases.update(set(group.releases))
    assert len(releases) == 3

    versions = {str(release.version) for release in releases}
    assert versions == {'1.7', '1.9', '1.11'}

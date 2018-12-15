# app
from .git.git import GitRepo
from .release import ReleaseRepo
from .warehouse import WareHouseRepo


__all__ = ['ReleaseRepo', 'WareHouseRepo', 'GitRepo', 'get_repo']


def get_repo(link=None):
    if link is None:
        return WareHouseRepo()
    if getattr(link, 'vcs', '') == 'git':
        return GitRepo(link)
    return ReleaseRepo(link=link)

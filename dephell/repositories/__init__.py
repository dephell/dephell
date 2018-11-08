from .release import ReleaseRepo
from .warehouse import WareHouseRepo
from .git.git import GitRepo


__all__ = ['ReleaseRepo', 'WareHouseRepo']


def get_repo(link=None):
    if link is None:
        return WareHouseRepo()
    if getattr(link, 'vcs') == 'git':
        return GitRepo(link)
    return ReleaseRepo(link=link)

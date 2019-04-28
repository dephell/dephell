# external
from dephell_links import DirLink, FileLink

# app
from .conda import CondaCloudRepo, CondaGitRepo, CondaRepo
from .git.git import GitRepo
from .local import LocalRepo
from .release import ReleaseRepo
from .warehouse import WareHouseRepo


__all__ = [
    'CondaCloudRepo',
    'CondaGitRepo',
    'CondaRepo',
    'get_repo',
    'GitRepo',
    'ReleaseRepo',
    'WareHouseRepo',
]


def get_repo(link=None):
    if link is None:
        return WareHouseRepo()
    if getattr(link, 'vcs', '') == 'git':
        return GitRepo(link)
    if isinstance(link, (DirLink, FileLink)):
        return LocalRepo(path=link.short)
    return ReleaseRepo(link=link)

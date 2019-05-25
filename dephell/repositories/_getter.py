# external
from dephell_links import DirLink, FileLink

# app
from ..config import config
from .conda import CondaCloudRepo, CondaGitRepo, CondaRepo
from .git.git import GitRepo
from .local import LocalRepo
from .release import ReleaseRepo
from .warehouse import WarehouseRepo, WarehouseAPIRepo


_repos = dict(
    conda_cloud=CondaCloudRepo,
    conda_git=CondaGitRepo,
    conda=CondaRepo,
    pypi=WarehouseAPIRepo,
)


def get_repo(link=None, name: str = None):
    if name is not None:
        return _repos[name]()

    if link is None:
        repo = WarehouseRepo()
        repo.add_repo(name='pypi', url=config['warehouse'])
        return repo

    if getattr(link, 'vcs', '') == 'git':
        return GitRepo(link)
    if isinstance(link, (DirLink, FileLink)):
        return LocalRepo(path=link.short)
    return ReleaseRepo(link=link)

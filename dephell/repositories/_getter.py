# external
from dephell_links import DirLink, FileLink

# app
from ..config import config
from ..constants import DEFAULT_WAREHOUSE
from .conda import CondaCloudRepo, CondaGitRepo, CondaRepo
from .git.git import GitRepo
from .local import LocalRepo
from .release import ReleaseRepo
from .warehouse import WarehouseRepo, WarehouseAPIRepo


_repos = dict(
    conda_cloud=CondaCloudRepo(),
    conda_git=CondaGitRepo(),
    conda=CondaRepo(),
    pypi=WarehouseAPIRepo(name='pypi', url=DEFAULT_WAREHOUSE),
)


def get_repo(link=None, name: str = None):
    if name is not None:
        return _repos[name]

    if link is None:
        repo = WarehouseRepo()
        for url in config['warehouse']:
            repo.add_repo(url=url)
        return repo

    if getattr(link, 'vcs', '') == 'git':
        return GitRepo(link)
    if isinstance(link, (DirLink, FileLink)):
        return LocalRepo(path=link.short)
    return ReleaseRepo(link=link)

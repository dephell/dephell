# external
from dephell_links import DirLink, FileLink

# app
from ..constants import DEFAULT_WAREHOUSE
from ._conda import CondaCloudRepo, CondaGitRepo, CondaRepo
from ._git.git import GitRepo
from ._local import LocalRepo
from ._release import ReleaseRepo
from ._warehouse import WarehouseAPIRepo


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
        from ..controllers import RepositoriesRegistry

        repo = RepositoriesRegistry()
        repo.attach_config()
        return repo

    if getattr(link, 'vcs', '') == 'git':
        return GitRepo(link)
    if isinstance(link, (DirLink, FileLink)):
        return LocalRepo(path=link.short)
    return ReleaseRepo(link=link)

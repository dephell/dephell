
from typing import Dict, Iterable, List

import attr

from ._base import CondaBaseRepo
from ._cloud import CondaCloudRepo
from ._git import CondaGitRepo


@attr.s()
class CondaRepo(CondaBaseRepo):
    channels = attr.ib(type=List[str], factory=list)
    git_repo = attr.ib(factory=CondaGitRepo)
    cloud_repo = attr.ib(factory=CondaCloudRepo)

    _requests = attr.ib(default=0)

    def __attrs_post_init__(self):
        if not self.git_repo.channels:
            self.git_repo.channels = self.channels
        if not self.cloud_repo.channels:
            self.cloud_repo.channels = self.channels

    def get_releases(self, dep) -> tuple:
        for repo in (self.cloud_repo, self.git_repo):
            releases = repo.get_releases(dep=dep)
            if releases:
                return releases
        return ()

    async def get_dependencies(self, *args, **kwargs):
        raise NotImplementedError('use get_releases to get deps')

    def search(self, query: Iterable[str]) -> List[Dict[str, str]]:
        return self.cloud_repo.search(query=query)

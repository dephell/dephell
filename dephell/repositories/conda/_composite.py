
from typing import List

import attr

from ._base import CondaBaseRepo
from ._cloud import CondaCloudRepo
from ._git import CondaGitRepo


@attr.s()
class CondaRepo(CondaBaseRepo):
    channels = attr.ib(type=List[str], factory=list)
    git_repo = attr.ib(factory=CondaGitRepo)
    cloud_repo = attr.ib(factory=CondaCloudRepo)

    def __attrs_post_init__(self):
        if not self.git_repo.channels:
            self.git_repo.channels = self.channels
        if not self.cloud_repo.channels:
            self.cloud_repo.channels = self.channels

    def get_releases(self, dep) -> tuple:
        releases = self.cloud_repo.get_releases(dep=dep)
        if releases:
            return releases
        return self.git_repo.get_releases(dep=dep)

    async def get_dependencies(self, *args, **kwargs):
        raise NotImplementedError('use get_releases to get deps')


from typing import List

import attr

from ._base import CondaBaseRepo
from ._git import CondaGitRepo


@attr.s()
class CondaRepo(CondaBaseRepo):
    channels = attr.ib(type=List[str], factory=list)
    git_repo = attr.ib(factory=CondaGitRepo)

    def __attrs_post_init__(self):
        if not self.git_repo.channels:
            self.git_repo.channels = self.channels

    def get_releases(self, dep) -> tuple:
        return self.git_repo.get_releases(dep=dep)

    async def get_dependencies(self, name: str, version: str, extra: str = None) -> tuple:
        return self.git_repo.get_dependencies(name=name, version=version, extra=extra)

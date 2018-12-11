# app
from .git_release import GitRelease


class GitSpecifier:
    def __contains__(self, release):
        return isinstance(release, GitRelease)

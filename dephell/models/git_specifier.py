# app
from .git_release import GitRelease


class GitSpecifier:
    def __contains__(self, release):
        return isinstance(release, GitRelease)

    def __iadd__(self, other):
        if hasattr(other, '_attach'):
            attached = other._attach(self)
            if attached:
                return other
        return NotImplemented

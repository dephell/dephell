# external
import attr

# app
from .release import Release


@attr.s(hash=False, eq=False, order=False)
class GitRelease(Release):
    commit = attr.ib(default=None)  # just for information

    def __eq__(self, other) -> str:
        if not isinstance(other, type(self)):
            return NotImplemented
        if self.name != other.name:
            return False
        if self.commit != other.commit:
            return False
        return True

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        left = (self.name, self.commit, self.version, self.time)
        right = (other.name, self.commit, other.version, other.time)
        return left < right

    def __hash__(self) -> int:
        return hash((self.name, self.commit, self.version))

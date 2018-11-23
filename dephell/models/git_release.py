# external
import attr

# app
from .release import Release


@attr.s(hash=False, cmp=True)
class GitRelease(Release):
    commit = attr.ib(default=None)  # just for information

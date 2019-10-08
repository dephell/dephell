# external
import attr

# app
from .release import Release


@attr.s(hash=False, eq=True, order=True)
class GitRelease(Release):
    commit = attr.ib(default=None)  # just for information

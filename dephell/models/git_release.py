import attr

from .release import Release


class GitRelease(Release):
    commit = attr.ib(default=None)  # just for information

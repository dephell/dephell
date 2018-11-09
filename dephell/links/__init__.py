# app
from .path import DirLink, FileLink
from .unknown import UnknownLink
from .url import URLLink
from .vcs import VCSLink


_links = (
    URLLink,
    DirLink,
    FileLink,
    VCSLink,
)


def parse_link(link):
    if not link:
        return
    for parser in _links:
        parsed = parser.parse(link)
        if parsed is not None:
            return parsed
    return UnknownLink(link)

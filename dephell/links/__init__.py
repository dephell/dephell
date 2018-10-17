from .path import DirLink, FileLink
from .url import URLLink
from .vcs import VCSLink
from .unknown import UnknownLink


_links = (
    URLLink,
    VCSLink,
    DirLink,
    FileLink,
)


def parse_link(link):
    if not link:
        return
    for parser in _links:
        parsed = parser.parse(link)
        if parsed is not None:
            return parsed
    return UnknownLink(link)

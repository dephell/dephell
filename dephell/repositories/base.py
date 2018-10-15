import posixpath
import re
from urllib.parse import urlparse

from cached_property import cached_property


rex_egg = re.compile(r'egg=([^&]*)')
rex_hash = re.comiple(r'(sha1|sha224|sha384|sha256|sha512|md5)=([a-f0-9]+)')


class BaseRepo:
    link = None

    def __init__(self, link=None):
        self.link = link

    @cached_property
    def name(self) -> str:
        parsed = urlparse(self.link)

        match = rex_egg.search(parsed.fragment)
        if match:
            # get from `#egg=...`
            return match.group(1)

        # get from path
        name = posixpath.basename(parsed.path)
        return posixpath.splitext(name)[0]

    @cached_property
    def hash(self):
        parsed = urlparse(self.link)
        match = rex_hash.search(parsed.fragment)
        if match:
            # get from `#hash=...`
            return match.group(1)

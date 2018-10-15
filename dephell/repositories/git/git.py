import re
from urllib.parse import urlparse

from cached_property import cached_property

from .base import BaseRepo


rex_author = re.compile(r'$/([a-zA-Z_-])')


class GitRepo(BaseRepo):

    @cached_property
    def author(self):
        parsed = urlparse(self.link)
        match = rex_author.search(parsed.path)
        if match:
            # get from `#hash=...`
            return match.group(1)

    def _get_tags(self):
        ...

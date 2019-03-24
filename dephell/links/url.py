# built-in
import re
from typing import Optional
from urllib.parse import unquote, urlparse


VERSION_SUFFIX_REX = re.compile(r'\-\d+$')


class URLLink:
    def __init__(self, link: str):
        self.short = link.split('#')[0]
        self.long = link

    @classmethod
    def parse(cls, link: str) -> Optional['URLLink']:
        if '@' in link:
            return
        if '.git' in link:
            return
        if link.startswith('file://'):
            return

        parsed = urlparse(link)
        if not parsed.scheme:
            return
        if not parsed.netloc:
            return
        # file extension required
        if '.' not in parsed.path.rstrip('/').rsplit('/', maxsplit=1)[-1]:
            return
        return cls(link)

    @property
    def name(self) -> Optional[str]:
        parsed = urlparse(self.short)
        if parsed.netloc in ('github.com', 'bitbucket.org', 'gitlab.com'):
            name = parsed.path.strip('/').split('/', maxsplit=2)[1]
            return name

        # get last part of path
        name = self.short.split('/')[-1]
        # drop all extensions, because in Python package name has no dots
        name = name.split('.')[0]
        # pip can return urlencoded name
        name = unquote(name)
        if not name:
            return None
        # drop version from the end
        if VERSION_SUFFIX_REX.search(name):
            name = VERSION_SUFFIX_REX.sub('', name, count=1)
        return name or None

    def __str__(self) -> str:
        return self.long

    def __repr__(self) -> str:
        return '{}({})'.format(type(self).__name__, str(self))

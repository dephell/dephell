# built-in
import os.path
from hashlib import sha256
from urllib.parse import unquote

# app
from ..utils import cached_property


class _PathLink:
    _check = NotImplemented

    def __init__(self, link):
        self.short = link.split('#')[0]
        self.long = link

    @classmethod
    def parse(cls, link):
        if '@' in link:
            return
        if link.startswith('file://'):
            link = link[len('file://'):]
        if '://' in link:
            return

        path = link.replace('/', os.path.sep).split('#')[0]
        if not cls._check(path):
            return

        return cls(link)

    @property
    def name(self):
        # get last part of path
        path = os.path.abspath(self.short.replace('/', os.path.sep))
        name = os.path.basename(path)

        # drop all extensions, because in Python package name has no dots
        name = name.split('.')[0]
        # pip can return urlencoded name
        name = unquote(name)
        return name or None

    @cached_property
    def hashes(self):
        with self.short.open('rb') as stream:
            content = stream.read()
        hasher = sha256()
        hasher.update(content)
        return 'sha256:' + hasher.digest()

    def __str__(self):
        return self.long


class FileLink(_PathLink):
    _check = os.path.isfile


class DirLink(_PathLink):
    _check = os.path.isdir

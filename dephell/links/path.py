import os.path
from urllib.parse import unquote
from os.path import sep


class _PathLink:
    _check = NotImplemented

    def __init__(self, link):
        self.link = link

    @classmethod
    def parse(cls, link):
        if '@' in link:
            return
        if link.startswith('file://'):
            link = link[len('file://'):]
        if '://' in link:
            return
        if cls._check(link.replace('/', sep)):
            return cls(link)

    @property
    def name(self):
        # get last part of path
        name = self.link.split('/')[-1]
        # drop all extensions, because in Python package name has no dots
        name = name.split('.')[0]
        # pip can return urlencoded name
        name = unquote(name)
        return name or None


class FileLink(_PathLink):
    _check = os.path.isfile


class DirLink(_PathLink):
    _check = os.path.isdir

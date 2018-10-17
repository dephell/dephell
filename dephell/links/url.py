from urllib.parse import unquote, urlparse


class URLLink:
    def __init__(self, link):
        self.link = link

    @classmethod
    def parse(cls, link):
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
    def name(self):
        # get last part of path
        name = self.link.split('/')[-1]
        # drop all extensions, because in Python package name has no dots
        name = name.split('.')[0]
        # pip can return urlencoded name
        name = unquote(name)
        return name or None

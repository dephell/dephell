from urllib.parse import unquote


class URLLink:
    def __init__(self, link):
        self.link = link

    @classmethod
    def parse(cls, link):
        if '@' in link:
            return
        if link.startswith('file://'):
            return
        if '://' not in link:
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

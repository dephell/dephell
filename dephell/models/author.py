# built-in
import re
from typing import Optional

# external
import attr


REX_AUTHOR = re.compile(r'^\s*(?P<name>.+?) \<(?P<mail>.+?)\>\s*$')


@attr.s()
class Author:
    name = attr.ib(type=str)
    mail = attr.ib(type=Optional[str], default=None)

    @classmethod
    def parse(cls, text: str) -> 'Author':
        match = REX_AUTHOR.match(text)
        if match is not None:
            return cls(**match.groupdict())
        return cls(name=text)

    def __str__(self) -> str:
        if not self.mail:
            return self.name
        return '{name} <{mail}>'.format(name=self.name, mail=self.mail)

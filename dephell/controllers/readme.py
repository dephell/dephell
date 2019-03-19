import re
from pathlib import Path
from typing import Optional
from string import Template

import attr
from m2r import convert
from cached_property import cached_property

from ..constants import EXTENSIONS


CODE = """
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, '${fname}'), encoding='utf-8') as stream:
    long_description = stream.read()
"""

REX_README_NAME = re.compile(r'(README\.[a-z]+)')


@attr.s()
class Readme:
    path = attr.ib(type=Path)

    @classmethod
    def discover(cls, path: Path) -> Optional['Readme']:
        for name in ('README', 'Readme', 'readme', 'ReadMe'):
            for ext in EXTENSIONS:
                fpath = (path / name).with_suffix(ext)
                if fpath.exists():
                    return cls(path=fpath)
        return None

    @classmethod
    def from_code(cls, path, content: str) -> Optional['Readme']:
        match = REX_README_NAME.search(content)
        if match is not None:
            return cls(path=path / match.groups()[0])
        return None

    @cached_property
    def markup(self) -> str:
        try:
            return EXTENSIONS[self.path.suffix()]
        except KeyError as e:
            raise ValueError('invalid readme extension: *.' + self.path.suffix()) from e

    @property
    def content_type(self) -> str:
        if self.markup == 'rst':
            return 'text/x-rst'
        if self.markup == 'md':
            return 'text/markdown'
        return 'text/plain'

    def as_rst(self) -> str:
        if self.markup == 'rst':
            return self.path.read_text()
        if self.markup == 'md':
            return convert(self.path.read_text())
        if self.markup == 'txt':
            return self.path.read_text()
        raise ValueError('invalid markup')

    def to_rst(self) -> 'Readme':
        if self.markup in ('txt', 'rst'):
            return self
        new_path = self.path.with_name(self.path.stem).with_suffix('rst')
        new_path.write_text(self.as_rst())
        return type(self)(path=new_path)

    def as_code(self) -> str:
        return Template(CODE).substitute(fname=self.path.name)

# built-in
import re
from pathlib import Path
from string import Template
from typing import Optional

# external
import attr
from m2r import convert

# app
from ..constants import EXTENSIONS
from ..utils import cached_property


CODE = """
import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, '${fname}'), 'rb') as stream:
    readme = stream.read().decode('utf8')
"""

REX_README_NAME = re.compile(r'(README\.[a-z]+)')


@attr.s()
class Readme:
    path = attr.ib(type=Path)

    @classmethod
    def discover(cls, path: Path) -> Optional['Readme']:
        for name in ('README', 'Readme', 'readme', 'ReadMe'):
            for ext in EXTENSIONS:
                if ext:
                    ext = '.' + ext
                fpath = (path / name).with_suffix(ext)
                if fpath.exists():
                    return cls(path=fpath)
        return None

    @classmethod
    def from_code(cls, path: Path, content: Optional[str] = None) -> Optional['Readme']:
        if content is None:
            content = path.read_text()
        match = REX_README_NAME.search(content)
        if match is None:
            return None
        new_path = path.parent / match.groups()[0]
        if not new_path.exists():
            return None
        return cls(path=new_path)

    @cached_property
    def markup(self) -> str:
        try:
            return EXTENSIONS[self.path.suffix.replace('.', '')]
        except KeyError as e:
            raise ValueError('invalid readme extension: *' + self.path.suffix) from e

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
            content = convert(self.path.read_text())
            content = content.replace('.. code-block:: toml', '.. code-block::')
            return content
        if self.markup == 'txt':
            return self.path.read_text()
        raise ValueError('invalid markup')

    def to_rst(self) -> 'Readme':
        if self.markup in ('txt', 'rst'):
            return self
        new_path = self.path.with_name(self.path.stem).with_suffix('.rst')
        new_path.write_text(self.as_rst())
        return type(self)(path=new_path)

    def as_code(self) -> str:
        return Template(CODE).substitute(fname=self.path.name)

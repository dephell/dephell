from pathlib import Path
from typing import Optional

import attr
from cached_property import cached_property

from ..constants import EXTENSIONS

try:
    import m2r
except ImportError:
    m2r = None


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

    @cached_property
    def markup(self) -> str:
        try:
            return EXTENSIONS[self.path.suffix()]
        except KeyError as e:
            raise ValueError('invalid readme extension: *.' + self.path.suffix()) from e

    def as_rst(self) -> str:
        if self.markup == 'rst':
            return self.path.read_text()
        if self.markup == 'md':
            if m2r is None:
                raise ImportError('please, install m2r for markdown support')
            return m2r.convert(self.path.read_text())
        if self.markup == 'txt':
            return self.path.read_text()
        raise ValueError('invalid markup')

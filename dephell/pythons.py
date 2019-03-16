import sys
from platform import python_version, python_implementation
from pathlib import Path
from typing import Iterator, Optional

import attr
from packaging.version import Version
from pythonfinder import Finder


__all__ = ['Python', 'Pythons']


finder = Finder()


@attr.s(slots=True)
class Python:
    path = attr.ib(type=Path)
    version = attr.ib(type=Version)
    implementation = attr.ib(type=str)


class Pythons:

    # PROPERTIES

    @property
    def current(self):
        return Python(
            path=sys.executable,
            version=Version(python_version()),
            implementation=python_implementation(),
        )

    # PUBLIC METHODS

    def get_best(self, constraint) -> Python:
        for python in self:
            if python.version in constraint:
                return python
        return self.current

    def get_by_version(self, version: Version) -> Optional[Python]:
        for python in self:
            if python.version == version:
                return python
        return None

    def get_by_name(self, name: str) -> Optional[Python]:
        for entry in finder.find_all_python_versions():
            if entry.name == name:
                return self._entry_to_python(entry)
        return None

    def get_by_path(self, path: Path) -> Optional[Python]:
        if not path.exists():
            return None
        for python in self:
            if path.samefile(python.path):
                return python
        return None

    # PRIVATE METHODS

    @staticmethod
    def _entry_to_python(entry) -> Python:
        return Python(
            path=entry.path,
            version=entry.py_version.version,
            # TODO: detect implementation (How? From path?)
            implementation=python_implementation(),
        )

    # MAGIC METHODS

    def __iter__(self) -> Iterator[Python]:
        for entry in finder.find_all_python_versions():
            yield self._entry_to_python(entry)

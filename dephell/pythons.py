import sys
import os
from platform import python_version, python_implementation
from pathlib import Path
from typing import Iterator, Optional, Union

import attr
from packaging.version import Version, InvalidVersion
from pythonfinder import Finder

from .constants import PYTHONS
from .models import RangeSpecifier


__all__ = ['Python', 'Pythons']


@attr.s(slots=True)
class Python:
    path = attr.ib(type=Path)
    version = attr.ib(type=Version)
    name = attr.ib(type=str)
    implementation = attr.ib(type=str)
    abstract = attr.ib(type=bool, default=False)


@attr.s(slots=True)
class Pythons:
    abstract = attr.ib(type=bool, default=False)
    finder = Finder()

    # PROPERTIES

    @property
    def current(self):
        return Python(
            path=Path(sys.executable),
            name=Path(sys.executable).name,
            version=Version(python_version()),
            implementation=python_implementation(),
        )

    # PUBLIC METHODS

    def get_best(self, prefer: Union[None, Path, Version, RangeSpecifier] = None) -> Python:
        # no preferentions
        if not prefer:
            return self.current

        # given version
        if isinstance(prefer, Version):
            python = self.get_by_version(prefer)
            if python is None:
                msg = 'cannot find interpreter for given python version: '
                raise FileNotFoundError(msg + str(prefer))
            return python

        # given path
        if isinstance(prefer, Path):
            python = self.get_by_path(prefer)
            if python is None:
                msg = 'cannot find binary by given path: '
                raise FileNotFoundError(msg + str(prefer))
            return python

        # given constraint
        if isinstance(prefer, RangeSpecifier):
            python = self.get_by_spec(prefer)
            if python is None:
                msg = 'cannot find interpreter for given constraint: '
                raise FileNotFoundError(msg + str(prefer))
            return python

        if not isinstance(prefer, str):
            raise TypeError('invalid python preferention type: ' + str(type(prefer)))

        # looks like a path
        path = Path(prefer)
        if os.path.sep in prefer and not path.exists():
            msg = 'cannot find binary by given path: '
            raise FileNotFoundError(msg + str(prefer))
        if path.exists():
            python = self.get_by_path(path)
            if python is not None:
                return python

        # looks like constraint
        if set(prefer) & {'<', '>', '='}:
            python = self.get_by_spec(RangeSpecifier(prefer))
            if python is not None:
                return python

        # ok, let's try it like a version
        try:
            version = Version(prefer)
        except InvalidVersion:
            pass
        else:
            python = self.get_by_version(version)
            if python is not None:
                return python

        # ok, let's try it like a name
        python = self.get_by_name(prefer)
        if python is not None:
            return python

        # no success
        raise FileNotFoundError('cannot find interpretor: ' + str(prefer))

    def get_by_spec(self, specifier: RangeSpecifier) -> Python:
        for python in self:
            if python.version in specifier:
                return python
        return self.current

    def get_by_version(self, version: Version) -> Optional[Python]:
        # exact version (3.7.1 -> 3.7.1)
        for python in self:
            if python.version == version:
                return python

        # base version (3.7 -> 3.7.1)
        for base_version in (version.release[:3], version.release[:2]):
            for python in self:
                if python.version.release[:2] == base_version:
                    return python
        return None

    def get_by_name(self, name: str) -> Optional[Python]:
        for python in self:
            if python.name == name:
                return python
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
            name=entry.name,
            version=entry.py_version.version,
            # TODO: detect implementation (How? From path?)
            implementation=python_implementation(),
        )

    # MAGIC METHODS

    def __iter__(self) -> Iterator[Python]:
        if not self.abstract:
            for entry in self.finder.find_all_python_versions():
                yield self._entry_to_python(entry)
            return

        # return non-abstract pythons
        returned = set()
        non_abstract = type(self)(abstract=False)
        for version in PYTHONS:
            python = non_abstract.get_by_version(Version(version))
            if python is not None:
                returned.add(version)
                yield python

        # return abstract pythons for all python versions not in this system
        for version in PYTHONS:
            if version in returned:
                continue
            path = self.current.path
            name = 'python' + version
            yield Python(
                path=path.parent / (name + path.suffix),
                version=Version(version),
                name=name,
                implementation=self.current.implementation,
                abstract=True,
            )

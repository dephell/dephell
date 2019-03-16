import sys
import os
from platform import python_version, python_implementation
from pathlib import Path
from typing import Iterator, Optional, Union

import attr
from packaging.version import Version, InvalidVersion
from pythonfinder import Finder

from .constants import PYTHONS
from .models import Constraint


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
            version=Version(python_version()),
            implementation=python_implementation(),
        )

    # PUBLIC METHODS

    def get_best(self, prefer: Union[None, Path, Version, Constraint] = None) -> Python:
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
        if isinstance(prefer, Constraint):
            python = self.get_by_constraint(prefer)
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
            python = self.get_by_constraint(Constraint(prefer))
            if python is not None:
                return python

        # ok, let's try it like a version
        try:
            version = Version(prefer)
        except InvalidVersion:
            pass
        else:
            python = self.get_by_name(version)
            if python is not None:
                return python

        # ok, let's try it like a name
        python = self.get_by_name(prefer)
        if python is not None:
            return python

        # no success
        raise FileNotFoundError('cannot find interpretor: ' + str(prefer))

    def get_by_constraint(self, constraint: Constraint) -> Python:
        for python in self:
            if python.version in constraint:
                return python
        return self.current

    def get_by_version(self, version: Version) -> Optional[Python]:
        # exact version (3.7.1 -> 3.7.1)
        for python in self:
            if python.version == version:
                return python

        # base version (3.7 -> 3.7.1)
        base_version = version.release[:2]
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

        non_abstract = type(self)(abstract=False)
        for version in PYTHONS:
            parsed_version = Version(version)
            # return non-abstract python if possible
            python = non_abstract.get_by_version(parsed_version)
            if python is not None:
                yield python
            else:
                # otherwise return abstract python
                path = self.current.path
                yield Python(
                    path=path.parent / 'python' + version + path.suffix,
                    version=version,
                    implementation=self.current.implementation,
                    abstract=True,
                )

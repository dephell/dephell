# built-in
import re
from pathlib import Path
from typing import Iterator, Optional

# external
from dephell_discover import Root
from packaging.version import VERSION_PATTERN


FILE_NAMES = (
    '__init__.py',
    '__version__.py',
    '__about__.py',
    '_version.py',
    '_about.py',
)
REX_VERSION = re.compile(VERSION_PATTERN, re.VERBOSE | re.IGNORECASE)
PREFIXES = {'__version__', 'VERSION', 'version'}


def get_version_from_file(path: Path) -> Optional[str]:
    with path.open('r') as stream:
        for line in stream:
            prefix, sep, version = line.partition('=')
            if not sep:
                continue
            if prefix.rstrip() not in PREFIXES:
                continue
            return version.strip().strip('\'"')
    return None


def get_version_from_project(project: Root) -> Optional[str]:
    for package in project.packages:
        for path in package:
            if path.name not in FILE_NAMES:
                continue
            version = get_version_from_file(path=path)
            if version:
                return version
    return None


def bump_file(path: Path, old: str, new: str) -> bool:
    file_bumped = False
    new_content = []
    with path.open('r') as stream:
        for line in stream:
            prefix, sep, _version = line.partition('=')
            if not sep:
                new_content.append(line)
                continue
            if prefix.rstrip() not in PREFIXES:
                new_content.append(line)
                continue

            # replace old version
            if old:
                new_line = line.replace(old, new, 1)
                if new_line != line:
                    new_content.append(new_line)
                    file_bumped = True
                    continue

            # replace any version
            new_line, count = REX_VERSION.subn(new, line)
            if count == 1:
                new_content.append(new_line)
                file_bumped = True
                continue

            new_content.append(line)
    if file_bumped:
        path.write_text(''.join(new_content))
    return file_bumped


def bump_project(project: Root, old: str, new: str) -> Iterator[Path]:
    for package in project.packages:
        for path in package:
            if path.name not in FILE_NAMES:
                continue
            file_bumped = bump_file(path=path, old=old, new=new)
            if file_bumped:
                yield path

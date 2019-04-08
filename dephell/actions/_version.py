import re
from pathlib import Path
from typing import List

from dephell_discover import Root
from packaging.version import Version

FILE_NAMES = (
    '__init__.py',
    '__version__.py',
    '__about__.py',
    '_version.py',
    '_about.py',
)
REX_VERSION = re.compile(r'\d+\.\d+(\.\d+)?')
PREFIXES = {'__version__', 'VERSION', 'version'}


def bump_file(path: Path, version: Version) -> bool:
    file_bumped = False
    new_content = []
    with path.open('r') as stream:
        for line in stream:
            prefix, sep, _version = line.partition('=')
            if not sep:
                continue
            if prefix.strip() not in PREFIXES:
                continue
            new_line, count = REX_VERSION.subn(str(version), line)
            if count == 1:
                new_content.append(new_line)
                file_bumped = True
            else:
                new_content.append(line)
    if file_bumped:
        path.write_text('\n'.join(new_content))
    return file_bumped


def bump_project(project: Root, version: Version) -> List[Path]:
    bumped_files = []
    for package in project.packages:
        for path in package:
            if path.name not in FILE_NAMES:
                continue
            file_bumped = bump_file(path=path, version=version)
            if file_bumped:
                bumped_files.append(path)
    return bumped_files

import re
from datetime import date
from pathlib import Path
from typing import List, Union

from dephell_discover import Root
from packaging.version import Version, VERSION_PATTERN

from .. import constants
from ._roman import arabic2roman, roman2arabic

FILE_NAMES = (
    '__init__.py',
    '__version__.py',
    '__about__.py',
    '_version.py',
    '_about.py',
)
REX_VERSION = re.compile(VERSION_PATTERN)
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


def bump_version(version: Union[Version, str], rule: str, scheme: str = 'semver') -> str:
    if scheme not in constants.VERSION_SCHEMES:
        raise ValueError('invalid scheme: {}'.format(scheme))
    if rule not in constants.VERSION_SCHEMES[scheme]:
        if REX_VERSION.fullmatch(rule):
            return rule
        raise ValueError('rule {} is unsupported by scheme {}'.format(rule, scheme))

    if scheme == 'roman':
        version = roman2arabic(version)
        return arabic2roman(version + 1)

    if isinstance(version, str):
        version = Version(version)

    if scheme in ('semver', 'pep'):
        parts = version.release + (0, 0)
        if rule in constants.VERSION_MAJOR:
            return '{}.0.0'.format(parts[0] + 1)
        if rule in constants.VERSION_MINOR:
            return '{}.{}.0'.format(parts[0], parts[1] + 1)
        if rule in constants.VERSION_PATCH:
            return '{}.{}.{}'.format(parts[0], parts[1], parts[2] + 1)

        if scheme == 'semver':
            if rule in constants.VERSION_PRE:
                pre = version.pre[1] if version.pre else 0
                return '{}.{}.{}-rc.{}'.format(*parts[:3], pre + 1)
            if rule in constants.VERSION_LOCAL:
                pre = '-{}.{}'.format(*version.pre) if version.pre else ''
                local = int(version.local) if version.local else 0
                return '{}.{}.{}{}+{}'.format(*parts[:3], pre, local + 1)

        if scheme == 'pep':
            if rule in constants.VERSION_PRE:
                pre = version.pre[1] if version.pre else 0
                return '{}.{}.{}rc{}'.format(*parts[:3], pre + 1)
            if rule in constants.VERSION_POST:
                # PEP allows post-releases for pre-releases,
                # but it "strongly discouraged", so let's ignore it.
                return '{}.{}.{}.post{}'.format(*parts[:3], (version.post or 0) + 1)
            if rule in constants.VERSION_DEV:
                if version.pre:
                    suffix = 'rc{}'.format(version.pre[1])
                elif version.post:
                    suffix = '.post{}'.format(version.post)
                else:
                    suffix = ''
                return '{}.{}.{}{}.dev{}'.format(*parts[:3], suffix, (version.dev or 0) + 1)
            if rule in constants.VERSION_LOCAL:
                old = str(version).split('+')[0]
                local = int(version.local) if version.local else 0
                return '{}+{}'.format(old, local + 1)

    if scheme == 'comver':
        parts = parts = version.release + (0,)
        if rule in constants.VERSION_MAJOR:
            return '{}.0'.format(parts[0] + 1)
        if rule in constants.VERSION_MINOR:
            return '{}.{}'.format(parts[0], parts[1] + 1)
        if rule in constants.VERSION_PRE:
            pre = version.pre[1] if version.pre else 0
            return '{}.{}-rc.{}'.format(*parts[:2], pre + 1)
        if rule in constants.VERSION_LOCAL:
            pre = '-{}.{}'.format(*version.pre) if version.pre else ''
            local = int(version.local) if version.local else 0
            return '{}.{}{}+{}'.format(*parts[:2], pre, local + 1)

    if scheme == 'calver':
        today = date.today()
        if rule in constants.VERSION_MAJOR:
            return '{}.{}'.format(today.year, today.month)
        if rule in constants.VERSION_PATCH:
            micro = (version.release + (0, 0))[2]
            micro = today.day if micro < today.day else micro + 1
            return '{}.{}.{}'.format(version.release[0], version.release[1], micro)

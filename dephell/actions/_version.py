# built-in
import re
from datetime import date
from pathlib import Path
from typing import Iterator, Optional, Union

# external
from dephell_discover import Root
from packaging.version import VERSION_PATTERN, Version

# app
from .. import constants
from ._roman import arabic2roman, roman2arabic


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


def bump_version(version: Union[Version, str], rule: str, scheme: str = 'semver') -> str:
    # check scheme
    if scheme not in constants.VERSION_SCHEMES:
        raise ValueError('invalid scheme: {}'.format(scheme))

    if rule == 'init':
        return constants.VERSION_INIT[scheme]

    # explicitly specified local version
    if rule[0] == '+':
        if 'local' not in constants.VERSION_SCHEMES[scheme]:
            raise ValueError('local numbers are unsupported by scheme ' + scheme)
        version = str(version).split('+')[0]
        return version + rule

    # check rule
    if rule not in constants.VERSION_SCHEMES[scheme]:
        if REX_VERSION.fullmatch(rule):
            return rule
        raise ValueError('rule {} is unsupported by scheme {}'.format(rule, scheme))

    if scheme == 'roman':
        version = roman2arabic(version)
        return arabic2roman(version + 1)

    if isinstance(version, str):
        version = Version(version)

    if scheme in ('semver', 'romver', 'pep', 'zerover'):
        parts = version.release + (0, 0)
        if scheme == 'zerover':
            parts = (0, ) + parts[1:]
        if rule in constants.VERSION_MAJOR:
            return '{}.0.0'.format(parts[0] + 1)
        if rule in constants.VERSION_MINOR:
            return '{}.{}.0'.format(parts[0], parts[1] + 1)
        if rule in constants.VERSION_PATCH:
            return '{}.{}.{}'.format(parts[0], parts[1], parts[2] + 1)

        if scheme in ('semver', 'romver', 'zerover'):
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
            if version.release[0] == today.year and version.release[1] == today.month:
                micro = (version.release + (0, 0))[2]
                micro = today.day if micro < today.day else micro + 1
            else:
                micro = today.day
            return '{}.{}.{}'.format(today.year, today.month, micro)

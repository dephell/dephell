import re
from typing import Dict

from ..base import Interface


# idk how this regex works
# source: conda/models/match_spec.py
REX_VERSION_BUILD = re.compile(r'((?:.+?)[^><!,|]?)(?:(?<![=!|,<>~])(?:[ =])([^-=,|<>~]+?))?$')


class CondaBaseRepo(Interface):

    @staticmethod
    def parse_req(req: str) -> Dict[str, str]:
        req = req.split('#', 1)[0]
        req = req.split(' if ', 1)[0]
        req = req.rsplit(':', 2)[-1]

        # TODO: parse url

        # extract name
        req = req.strip()
        positions = [req.find(char) for char in '=<>!~ ']
        positions = [pos for pos in positions if pos >= 0]
        if positions:
            version_start = min(positions)
            name, req = req[:version_start], req[version_start:]
        else:
            name, req = req, ''
        name = name.strip()
        req = req.strip()
        if not req:
            return dict(name=name)

        # extract version and build
        match = REX_VERSION_BUILD.search(req)
        if match:
            version, build = match.groups()
            if version is None:
                version = ''
            if build is None:
                build = ''
        else:
            version, build = req, ''
        version = version.strip()
        build = build.strip()

        # transform version to specifier
        if version[0] == '=' and version[1] != '=':
            version = '==' + version[1:]
        elif version[0] not in '=<>!~':
            version = '==' + version

        result = dict(name=name)
        if version:
            result['version'] = version
        if build:
            result['build'] = build
        return result

import re
from collections import defaultdict
from typing import Tuple, Optional, Union, List, Dict
from xml.etree import ElementTree

import attr
import requests
from cached_property import cached_property
from dephell_specifier import RangeSpecifier
from packaging.version import Version, VERSION_PATTERN


RSS_URL = 'https://snyk.io/vuln/feed.xml?type=pip'
REX_VERSION = re.compile(VERSION_PATTERN, re.VERBOSE | re.IGNORECASE)
REX_TAG = re.compile(r'<[a-z]+.*?>')
REX_LINK = re.compile(r'https?\:\/\/[a-z]+[^\s\"]+')


@attr.s(slots=True)
class SnykVulnInfo:
    name = attr.ib(type=str)
    severity = attr.ib(type=str)
    description = attr.ib(type=str)
    version = attr.ib(type=Optional[Version])
    links = attr.ib(type=Tuple[str, ...])

    @property
    def specifier(self) -> RangeSpecifier:
        return RangeSpecifier('<' + self.version)


@attr.s()
class Snyk:
    """
    https://snyk.io/vuln?type=pip
    """
    url = attr.ib(type=str, default=RSS_URL)

    @cached_property
    def vulns(self) -> Dict[str, List[SnykVulnInfo]]:
        response = requests.get(self.url)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)

        result = defaultdict(list)
        for item in root[0]:
            if item.tag != 'item':
                continue
            item = {field.tag: field.text for field in item}
            desc = self._parse_description(item['description'])

            versions = [Version(version) for version in desc['versions'] if version]
            version = max(versions) if versions else None

            result[desc['name']].append(SnykVulnInfo(
                name=desc['name'],
                severity=desc['severity'],
                description=item['title'].split('https://snyk.io/')[0],
                version=version,
                links=tuple(desc['links']),
            ))

        return result

    def _parse_description(self, text: str):
        result = dict(links=[], versions=[])
        for line in text.splitlines():
            clean = REX_TAG.sub('', line.strip())
            if clean.startswith('Severity:'):
                result['severity'] = clean.split()[1]
                continue
            if clean.startswith('Affects:'):
                result['name'] = clean.split()[1]
                continue
            if ' or higher' in clean:
                result['versions'] = sum(REX_VERSION.findall(clean), ())
            result['links'].extend(REX_LINK.findall(line))
        return result

    def get(self, name: str, version: Union[str, Version]) -> List[SnykVulnInfo]:
        if type(version) is str:
            version = Version(version)
        vulns = []
        for vuln in self.vulns.get(name, []):
            if vuln.version is None or version < vuln.version:
                vulns.append(vuln)
        return vulns

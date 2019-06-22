# built-in
import re
from typing import Dict, List, Tuple, Union

# external
import attr
import requests
from dephell_specifier import RangeSpecifier
from packaging.version import Version

# app
from ..cache import JSONCache
from ..cached_property import cached_property


DUMP_URL = 'https://github.com/pyupio/safety-db/raw/master/data/insecure_full.json'
REX_LINK = re.compile(r'https?\:\/\/[a-z]+[^\s\"]+')


@attr.s(slots=True)
class SafetyVulnInfo:
    name = attr.ib(type=str)
    description = attr.ib(type=str)
    links = attr.ib(type=Tuple[str, ...])
    specifier = attr.ib(type=RangeSpecifier)


@attr.s()
class Safety:
    """
    https://pyup.io/
    https://github.com/pyupio/safety-db
    """
    url = attr.ib(type=str, default=DUMP_URL)

    @cached_property
    def vulns(self) -> Dict[str, Tuple[SafetyVulnInfo, ...]]:
        cache = JSONCache('pyup.io', ttl=3600 * 24)
        records = cache.load()
        if records is None:
            response = requests.get(self.url)
            response.raise_for_status()
            records = response.json()
            cache.dump(records)

        vulns = dict()
        for name, subrecords in records.items():
            package_vulns = []
            for record in subrecords:
                links = tuple(REX_LINK.findall(record['advisory']))
                description = REX_LINK.sub('', record['advisory'])
                if record['cve']:
                    link = 'https://nvd.nist.gov/vuln/detail/' + record['cve']
                    links += (link, )
                package_vulns.append(SafetyVulnInfo(
                    name=name,
                    description=description,
                    links=links,
                    specifier=RangeSpecifier(' || '.join(record['specs'])),
                ))
            vulns[name] = tuple(package_vulns)
        return vulns

    def get(self, name: str, version: Union[str, Version]) -> List[SafetyVulnInfo]:
        if type(version) is str:
            version = Version(version)
        vulns = []
        for vuln in self.vulns.get(name, []):
            if version in vuln.specifier:
                vulns.append(vuln)
        return vulns

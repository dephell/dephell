from typing import Dict, List, Tuple, Optional, Union

import attr
import requests
from packaging.version import Version
from dephell_specifier import RangeSpecifier


from ..cache import JSONCache
from ..utils import cached_property


DUMP_URL = 'https://github.com/pyupio/safety-db/raw/master/data/insecure_full.json'


@attr.s(slots=True)
class VulnInfo:
    name = attr.ib(type=str)
    description = attr.ib(type=str)
    specifier = attr.ib(type=RangeSpecifier)

    cve = attr.ib(type=Optional[str], default=None)


@attr.s()
class Safety:
    url = attr.ib(type=str, default=DUMP_URL)

    @cached_property
    def vulns(self) -> Dict[str, Tuple[VulnInfo, ...]]:
        cache = JSONCache('safety', ttl=3600 * 24)
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
                package_vulns.append(VulnInfo(
                    name=name,
                    description=record['advisory'],
                    specifier=RangeSpecifier(' || '.join(record['specs'])),
                    cve=record['cve'],
                ))
            vulns[name] = tuple(package_vulns)
        return vulns

    def get(self, name: str, version: Union[str, Version]) -> List[VulnInfo]:
        if type(version) is str:
            version = Version(version)
        vulns = []
        for vuln in self.vulns.get(name, []):
            if version in vuln.specifier:
                vulns.append(vuln)
        return vulns

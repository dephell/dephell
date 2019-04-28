import json
import sys
from bz2 import BZ2Decompressor
from collections import defaultdict
from datetime import datetime
from platform import uname
from typing import Any, Dict, List, Iterator

import attr
import requests
from dephell_specifier import RangeSpecifier
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


from ._base import CondaBaseRepo
from ...cache import JSONCache
from ...config import config
from ...models.release import Release
from ...utils import cached_property


# https://conda.anaconda.org/conda-forge/linux-64
# https://conda.anaconda.org/conda-forge/noarch
# https://repo.anaconda.com/pkgs/main/linux-64
# https://repo.anaconda.com/pkgs/main/noarch
# https://repo.anaconda.com/pkgs/free/linux-64
# https://repo.anaconda.com/pkgs/free/noarch
# https://repo.anaconda.com/pkgs/r/linux-64
# https://repo.anaconda.com/pkgs/r/noarch


@attr.s()
class CondaCloudRepo(CondaBaseRepo):
    channels = attr.ib(type=List[str], factory=list)

    _repo_url = 'https://conda.anaconda.org/{channel}/{arch}/repodata.json.bz2'
    _default_url = 'https://repo.anaconda.com/pkgs/{channel}/{arch}/repodata.json.bz2'

    def get_releases(self, dep) -> tuple:
        raw_releases = self._json.get(dep.name)
        if raw_releases is None:
            return ()
        releases = []
        for version, release_info in raw_releases.items():
            release = Release(
                raw_name=dep.raw_name,
                version=version,
                time=datetime.fromtimestamp(release_info['timestamp']),
                hashes=tuple(file['sha256'] for file in release_info['files'] if file['sha256'])
            )

            # get deps
            deps = []
            for req in release_info['depends']:
                parsed = self.parse_req(req)
                if parsed['name'] == 'python':
                    release.python = RangeSpecifier(parsed.get('version', '*'))
                    continue
                req = parsed['name'] + parsed.get('version', '')
                deps.append(Requirement(req))
            release.dependencies = tuple(deps)

            releases.append(release)
        return tuple(releases)

    async def get_dependencies(self, *args, **kwargs):
        raise NotImplementedError('use get_releases to get deps')

    # hidden methods

    def _get_urls(self, channel: str) -> Iterator[str]:
        translation = {
            'Linux': 'linux',
            'Windows': 'win',
            'darwin': 'osx',
        }
        system = translation.get(uname().system, 'linux')
        system += '-64' if sys.maxsize > 2**32 else '-32'
        for arch in (system, 'noarch'):
            if channel == 'defaults':
                for channel in ('main', 'free'):
                    yield self._default_url.format(arch=arch, channel=channel)
            else:
                yield self._repo_url.format(arch=arch, channel=channel)

    @cached_property
    def _json(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        channels = list(self.channels)
        if 'defaults' not in channels:
            channels.append('defaults')

        all_deps = defaultdict(dict)
        for channel in channels:
            cache = JSONCache('conda', 'cloud', channel, ttl=config['cache']['ttl'])
            channel_deps = cache.load()
            if channel_deps is not None:
                for dep, releases in channel_deps.items():
                    all_deps[dep].update(releases)
                continue

            channel_deps = defaultdict(dict)
            for url in self._get_urls(channel=channel):
                response = requests.get(url)
                response.raise_for_status()
                content = BZ2Decompressor().decompress(response.content).decode('utf-8')
                base_url = url.rsplit('/', 1)[0]
                for fname, info in json.loads(content)['packages'].items():
                    # release info
                    name = canonicalize_name(info.pop('name'))
                    version = info.pop('version')
                    if version not in channel_deps[name]:
                        channel_deps[name][version] = dict(
                            depends=info['depends'],
                            license=info.get('license', 'unknown'),
                            timestamp=info.get('timestamp', 0) // 1000,
                            channel=channel,
                            files=[],
                        )
                    # file info
                    channel_deps[name][version]['files'].append(dict(
                        url=base_url + '/' + fname,
                        sha256=info.get('sha256', None),
                        size=info['size'],
                    ))

            cache.dump(channel_deps)
            for dep, releases in channel_deps.items():
                all_deps[dep].update(releases)

        return dict(all_deps)

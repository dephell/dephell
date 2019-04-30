import json
import sys
from bz2 import BZ2Decompressor
from collections import defaultdict, OrderedDict
from datetime import datetime
from logging import getLogger
from platform import uname
from typing import Any, Dict, List, Iterator, Iterable

import attr
import requests
from dephell_specifier import RangeSpecifier
from packaging.version import parse
from packaging.utils import canonicalize_name


from ._base import CondaBaseRepo
from ...cache import JSONCache
from ...config import config
from ...models.release import Release
from ...models.simple_dependency import SimpleDependency
from ...utils import cached_property


# https://conda.anaconda.org/conda-forge/linux-64
# https://conda.anaconda.org/conda-forge/noarch
# https://repo.anaconda.com/pkgs/main/linux-64
# https://repo.anaconda.com/pkgs/main/noarch
# https://repo.anaconda.com/pkgs/free/linux-64
# https://repo.anaconda.com/pkgs/free/noarch
# https://repo.anaconda.com/pkgs/r/linux-64
# https://repo.anaconda.com/pkgs/r/noarch

URL_FIELDS = {
    'home': 'homepage',
    'dev_url': 'repository',
    'doc_url': 'documentation',
    'license_url': 'license',
    'source_url': 'source',
}

logger = getLogger('dephell.repositories.conda.cloud')


@attr.s()
class CondaCloudRepo(CondaBaseRepo):
    channels = attr.ib(type=List[str], factory=list)

    # https://conda.anaconda.org/{channel}/channeldata.json
    _user_urls = dict(
        repo='https://conda.anaconda.org/{channel}/{arch}/repodata.json.bz2',
        chan='https://conda.anaconda.org/{channel}/channeldata.json',
    )
    _main_urls = dict(
        repo='https://repo.anaconda.com/pkgs/{channel}/{arch}/repodata.json.bz2',
        chan='https://repo.anaconda.com/pkgs/main/channeldata.json',
    )
    _search_url = 'https://api.anaconda.org/search'

    _allowed_values = dict(
        type=frozenset({'conda', 'pypi', 'env', 'ipynb'}),
        platform=frozenset({
            'osx-32', 'osx-64',
            'win-32', 'win-64',
            'linux-32', 'linux-64',
            'linux-armv6l', 'linux-armv7l', 'linux-ppc64le',
            'noarch',
        }),
    )

    def get_releases(self, dep) -> tuple:
        self._update_dep(dep=dep)

        raw_releases = self._releases.get(dep.name)
        if not raw_releases:
            return ()
        raw_releases = OrderedDict(sorted(
            raw_releases.items(),
            key=lambda rel: parse(rel[0]),
            reverse=True,
        ))

        releases = []
        for version, release_info in raw_releases.items():
            release = Release(
                raw_name=dep.raw_name,
                version=version,
                time=datetime.fromtimestamp(release_info['timestamp']),
                hashes=tuple(file['sha256'] for file in release_info['files'] if file['sha256']),
            )

            # get deps
            deps = set()
            pythons = set()
            for req in release_info['depends']:
                parsed = self.parse_req(req)
                if parsed['name'] == 'python':
                    if 'version' in parsed:
                        pythons.add(parsed['version'])
                    continue
                deps.add(SimpleDependency(
                    name=parsed['name'],
                    specifier=parsed.get('version', '*'),
                ))
            release.python = RangeSpecifier(' || '.join(pythons))
            release.dependencies = tuple(sorted(deps))

            releases.append(release)
        return tuple(releases)

    async def get_dependencies(self, *args, **kwargs):
        raise NotImplementedError('use get_releases to get deps')

    def search(self, query: Iterable[str]) -> List[Dict[str, str]]:
        fields = self._parse_query(query=query)
        logger.debug('search on anaconda cloud', extra=dict(query=fields))
        invalid_fields = set(fields) - {'name', 'type', 'platform'}
        if invalid_fields:
            raise ValueError('Invalid fields: {}'.format(', '.join(invalid_fields)))
        if 'name' not in fields:
            raise ValueError('please, specify search text')
        for field, value in fields.items():
            if field in self._allowed_values and value not in self._allowed_values[field]:
                raise ValueError('invalid {field} value. Given: {given}. Allowed: {allowed}'.format(
                    field=field,
                    given=value,
                    allowed=', '.join(self._allowed_values[field]),
                ))

        response = requests.get(self._search_url, params=fields)
        response.raise_for_status()

        results = []
        for info in response.json():
            urls = dict(anaconda=info['html_url'])
            for field, value in info.items():
                if value and value != 'None' and field in URL_FIELDS:
                    urls[URL_FIELDS[field]] = value
            results.append(dict(
                name=info['name'],
                version=info['versions'][-1],
                description=info['summary'],
                license=info['license'],
                channel=info['owner'],
                links=urls,
            ))
        return results

    # hidden methods

    def _get_chan_url(self, channel: str) -> str:
        if channel == 'defaults':
            return self._main_urls['chan'].format(channel=channel)
        return self._user_urls['chan'].format(channel=channel)

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
                    yield self._main_urls['repo'].format(arch=arch, channel=channel)
            else:
                yield self._user_urls['repo'].format(arch=arch, channel=channel)

    def _update_dep(self, dep) -> None:
        info = self._packages.get(dep.name)
        if not info:
            return
        if not dep.links:
            dep.links = info['links']
        if not dep.license and 'license' in info:
            dep.license = self._get_license(info['license'])
        if not dep.description and 'summary' in info:
            dep.description = info['summary']

    # hidden properties

    @cached_property
    def _channels(self) -> List[str]:
        channels = list(self.channels)
        if not channels:
            channels.append('conda-forge')
        if 'defaults' not in channels:
            channels.append('defaults')
        return channels[::-1]

    @cached_property
    def _packages(self) -> Dict[str, Dict[str, Any]]:
        all_packages = dict()
        for channel in self._channels:
            cache = JSONCache('conda', 'cloud', channel, 'packages', ttl=config['cache']['ttl'])
            channel_packages = cache.load()
            if channel_packages is not None:
                all_packages.update(channel_packages)
                continue

            url = self._get_chan_url(channel=channel)
            response = requests.get(url)
            response.raise_for_status()
            channel_packages = dict()
            for name, info in response.json()['packages'].items():
                name = canonicalize_name(name)
                links = dict(
                    anaconda='https://anaconda.org/{channel}/{name}'.format(
                        channel=channel,
                        name=name,
                    ),
                )
                for field, value in info.items():
                    if value and value != 'None' and field in URL_FIELDS:
                        links[URL_FIELDS[field]] = value
                channel_packages[name] = dict(
                    channel=channel,
                    links=links,
                )
                license = info.get('license')
                if license and license.lower() not in ('none', 'unknown'):
                    channel_packages[name]['license'] = license
                summary = info.get('summary')
                if summary:
                    channel_packages[name]['summary'] = summary

            all_packages.update(channel_packages)
            cache.dump(channel_packages)

        return all_packages

    @cached_property
    def _releases(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        all_deps = defaultdict(dict)
        for channel in self._channels:
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
                            depends=set(),
                            timestamp=info.get('timestamp', 0) // 1000,
                            files=[],
                        )
                    # file info
                    channel_deps[name][version]['depends'].update(info['depends'])
                    channel_deps[name][version]['files'].append(dict(
                        url=base_url + '/' + fname,
                        sha256=info.get('sha256', None),
                        size=info['size'],
                    ))

            for dep, releases in channel_deps.items():
                for release in releases.values():
                    release['depends'] = list(release['depends'])
                all_deps[dep].update(releases)
            cache.dump(channel_deps)

        return dict(all_deps)

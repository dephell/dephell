# built-in
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional, Tuple
from urllib.parse import urlparse

# external
import aiofiles
import requests
from aiohttp import ClientSession
from dephell_markers import Markers
from packaging.requirements import Requirement

# project
import attr

# app
from ..cache import JSONCache, TextCache
from ..config import config
from ..models.author import Author
from ..models.release import Release
from .base import Interface


def _process_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.path in ('', '/', '/simple', '/simple/'):
        path = '/pypi/'
    else:
        path = parsed.path
    if parsed.hostname == 'pypi.python.org':
        hostname = 'pypi.org'
    else:
        hostname = parsed.hostname
    return parsed.scheme + '://' + hostname + path


@attr.s()
class WareHouseRepo(Interface):
    name = attr.ib(default='pypi')
    url = attr.ib(type=str, factory=lambda: config['warehouse'], converter=_process_url)
    prereleases = attr.ib(type=bool, default=False)  # allow prereleases

    hash = None
    link = None

    @property
    def pretty_url(self):
        parsed = urlparse(self.url)
        path = '/simple/' if parsed.path == '/pypi/' else parsed.path
        return parsed.scheme + '://' + parsed.hostname + path

    def get_releases(self, dep) -> tuple:
        # retrieve data
        cache = JSONCache('releases', dep.base_name, ttl=config['cache']['ttl'])
        data = cache.load()
        if data is None:
            url = '{url}{name}/json'.format(url=self.url, name=dep.base_name)
            response = requests.get(url)
            if response.status_code == 404:
                raise KeyError('project {name} is not found'.format(name=dep.base_name))
            data = response.json()
            cache.dump(data)
        elif isinstance(data, str) and data == '':
            return ()

        # update info for dependency
        self._update_dep_from_data(dep=dep, data=data['info'])

        # init releases
        releases = []
        for version, info in data['releases'].items():
            # ignore version if no files for release
            if not info:
                continue
            release = Release.from_response(
                name=dep.base_name,
                version=version,
                info=info,
                extra=dep.extra,
            )
            # filter prereleases if needed
            if release.version.is_prerelease and not self.prereleases:
                continue
            releases.append(release)
        releases.sort(reverse=True)
        return tuple(releases)

    async def get_dependencies(self, name: str, version: str,
                               extra: Optional[str] = None) -> Tuple[Requirement, ...]:
        cache = TextCache('deps', name, str(version))
        deps = cache.load()
        if deps is None:
            task = self._get_from_json(name=name, version=version)
            deps = await asyncio.gather(asyncio.ensure_future(task))
            deps = deps[0]
            cache.dump(deps)
        elif deps == ['']:
            return ()

        # filter result
        result = []
        for dep in deps:
            req = Requirement(dep)
            dep_extra = req.marker and Markers(req.marker).extra
            # it's not extra and we want not extra too
            if dep_extra is None and extra is None:
                result.append(req)
                continue
            # it's extra, but we want not the extra
            # or it's not the extra, but we want extra.
            if dep_extra is None or extra is None:
                continue
            # it's extra and we want this extra
            elif dep_extra == extra:
                result.append(req)
                continue

        return tuple(result)

    # private methods

    @staticmethod
    def _update_dep_from_data(dep, data: dict) -> None:
        """Updates metadata for dependency from json response
        """
        if not dep.description:
            dep.description = data['summary']

        if not dep.authors:
            dep.authors = []
            if data['author']:
                dep.authors.append(Author(
                    name=data['author'],
                    mail=data.get('author_email') or None,
                ))
            if data['maintainer']:
                dep.authors.append(Author(
                    name=data['maintainer'],
                    mail=data.get('maintainer_email') or None,
                ))
            dep.authors = tuple(dep.authors)

        if not dep.links:
            if data['project_urls']:
                dep.links = {k.lower(): v for k, v in data['project_urls'].items()}
            if data['package_url'] and data['package_url'] not in dep.links.values():
                dep.links['package'] = data['package_url']
            if data['project_url'] and data['project_url'] not in dep.links.values():
                dep.links['project'] = data['project_url']

        if not dep.classifiers:
            dep.classifiers = tuple(data['classifiers'])
        if not dep.license and data['license'] not in ('UNKNOWN', '', None):
            dep.license = data['license']

    async def _get_from_json(self, *, name, version):
        url = '{url}{name}/{version}/json'.format(
            url=self.url,
            name=name,
            version=version,
        )
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError('invalid response: {} {} ({})'.format(
                        response.status, response.reason, url,
                    ))
                response = await response.json()
        dist = response['info']['requires_dist'] or []
        if dist:
            return dist

        # If no requires_dist then package metadata can be broken.
        # Let's check distribution files.
        return await self._get_from_files(response['urls'])

    async def _get_from_files(self, files_info: List[dict]) -> Tuple[str, ...]:
        if not files_info:
            return ()

        from ..converters import SDistConverter, WheelConverter

        sdist = SDistConverter()
        wheel = WheelConverter()
        rules = (
            (wheel, lambda info: info['packagetype'] == 'bdist_wheel'),
            (sdist, lambda info: info['packagetype'] == 'sdist'),
            (wheel, lambda info: info['url'].endswith('.whl')),
            (sdist, lambda info: info['url'].endswith('.tar.gz')),
            (sdist, lambda info: info['url'].endswith('.zip')),
        )

        for converer, checker in rules:
            for file_info in files_info:
                if checker(file_info):
                    return await self._download_and_parse(url=file_info['url'], converter=converer)
        return ()

    async def _download_and_parse(self, *, url: str, converter) -> Tuple[str, ...]:
        with TemporaryDirectory() as tmp:
            async with ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError('invalid response: {} {} ({})'.format(
                            response.status, response.reason, url,
                        ))
                    path = Path(tmp) / url.rsplit('/', maxsplit=1)[-1]
                    async with aiofiles.open(str(path), mode='wb') as stream:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            await stream.write(chunk)
            root = converter.load(path)
            return tuple(str(dep) for dep in root.dependencies)

# built-in
import asyncio
import posixpath
from logging import getLogger
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import urlparse, urljoin
from xmlrpc.client import ServerProxy

# external
import attr
import requests
from dephell_licenses import License, licenses
from packaging.requirements import Requirement

# app
from ...cache import JSONCache, TextCache
from ...config import config
from ...exceptions import PackageNotFoundError, InvalidFieldsError
from ...models.author import Author
from ...models.release import Release
from ...networking import aiohttp_session
from ._base import WarehouseBaseRepo


logger = getLogger('dephell.repositories')
_fields = {
    'author_email',
    'author',
    'description',
    'download_url',
    'home_page',
    'keywords',
    'license',
    'maintainer_email',
    'maintainer',
    'name',
    'platform',
    'summary',
    'version',
}


@attr.s()
class WarehouseAPIRepo(WarehouseBaseRepo):
    name = attr.ib(type=str)
    url = attr.ib(type=str)
    auth = attr.ib(default=None)

    prereleases = attr.ib(type=bool, factory=lambda: config['prereleases'])  # allow prereleases
    from_config = attr.ib(type=bool, default=False)

    propagate = True
    hash = None
    link = None

    def __attrs_post_init__(self):
        # make name canonical
        if self.name in ('pypi.org', 'pypi.python.org'):
            self.name = 'pypi'

        # replace link on simple index by link on pypi api
        parsed = urlparse(self.url)
        if parsed.path in ('', '/', '/simple', '/simple/'):
            path = '/pypi/'
        else:
            path = parsed.path
        if parsed.hostname == 'pypi.python.org':
            hostname = 'pypi.org'
        else:
            hostname = parsed.hostname
        self.url = parsed.scheme + '://' + hostname + path

    @property
    def pretty_url(self):
        parsed = urlparse(self.url)
        path = '/simple/' if parsed.path == '/pypi/' else parsed.path
        return parsed.scheme + '://' + parsed.hostname + path

    def get_releases(self, dep) -> tuple:
        # retrieve data
        cache = JSONCache(
            'warehouse-api', urlparse(self.url).hostname, 'releases', dep.base_name,
            ttl=config['cache']['ttl'],
        )
        data = cache.load()
        if data is None:
            url = '{url}{name}/json'.format(url=self.url, name=dep.base_name)
            response = requests.get(url, auth=self.auth)
            if response.status_code == 404:
                raise PackageNotFoundError(package=dep.base_name, url=url)
            data = response.json()
            cache.dump(data)
        elif isinstance(data, str) and data == '':
            return ()

        # update info for dependency
        self._update_dep_from_data(dep=dep, data=data['info'])

        # init releases
        releases = []
        prereleases = []
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
            if release.version.is_prerelease:
                prereleases.append(release)
                if not self.prereleases and not dep.prereleases:
                    continue

            releases.append(release)

        # special case for black: if there is no releases, but found some
        # prereleases, implicitly allow prereleases for this package
        if not releases and prereleases:
            releases = prereleases

        releases.sort(reverse=True)
        return tuple(releases)

    async def get_dependencies(self, name: str, version: str,
                               extra: Optional[str] = None) -> Tuple[Requirement, ...]:
        cache = TextCache('warehouse-api', urlparse(self.url).hostname, 'deps', name, str(version))
        deps = cache.load()
        if deps is None:
            task = self._get_from_json(name=name, version=version)
            deps = await asyncio.gather(asyncio.ensure_future(task))
            deps = deps[0]
            cache.dump(deps)
        elif deps == ['']:
            return ()
        return self._convert_deps(deps=deps, name=name, version=version, extra=extra)

    def search(self, query: Iterable[str]) -> List[Dict[str, str]]:
        fields = self._parse_query(query=query)
        logger.debug('search on PyPI', extra=dict(query=fields))
        invalid_fields = set(fields) - _fields
        if invalid_fields:
            raise InvalidFieldsError(fields=invalid_fields)

        with ServerProxy('https://pypi.org/pypi') as client:
            response = client.search(fields, 'and')

        results = []
        for info in response:
            results.append(dict(
                name=info['name'],
                version=info['version'],
                description=info['summary'],
                url='https://pypi.org/project/{}/'.format(info['name']),
            ))
        return results

    async def download(self, name: str, version: str, path: Path) -> bool:
        # retrieve data
        cache = JSONCache(
            'warehouse-api', urlparse(self.url).hostname, 'releases', name,
            ttl=config['cache']['ttl'],
        )
        response = cache.load()
        if response is None:
            url = urljoin(self.url, posixpath.join(name, str(version), 'json'))
            async with aiohttp_session(auth=self.auth) as session:
                async with session.get(url) as response:
                    if response.status == 404:
                        raise PackageNotFoundError(package=name, url=url)
                    response.raise_for_status()
                    response = await response.json()
                    cache.dump(response)

        exts = ('py3-none-any.whl', '-none-any.whl', '.whl', '.tar.gz', '.zip')
        for ext in exts:
            for link in response['urls']:
                if not link['filename'].endswith(ext):
                    continue
                if path.is_dir():
                    path = path / link['filename']
                await self._download(url=link['url'], path=path)
                return True
        return False

    # private methods

    @classmethod
    def _update_dep_from_data(cls, dep, data: dict) -> None:
        """Updates metadata for dependency from json response
        """
        # if name contains dot, restore it, because setuptools can't process it
        if '.' in data['name']:
            dep.raw_name = data['name']
            if 'name' in dep.__dict__:
                del dep.__dict__['name']

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

        if not dep.license:
            dep.license = cls._get_license(data)

    @staticmethod
    def _get_license(data: dict) -> Union[str, License, None]:
        license_classifier = None
        for classifier in data['classifiers']:
            if classifier.startswith('License :: '):
                license_classifier = classifier.split(' :: ')[-1].strip()
                license = licenses.get_by_classifier(classifier)
                if license is not None:
                    return license

        if data['license'] in ('UNKNOWN', '', None):
            return license_classifier

        license = licenses.get_by_id(data['license'])
        if license is not None:
            return license

        license = licenses.get_by_name(data['license'])
        if license is not None:
            return license

        if license_classifier:
            return license_classifier
        return data['license']

    async def _get_from_json(self, *, name, version):
        url = urljoin(self.url, posixpath.join(name, str(version), 'json'))
        async with aiohttp_session(auth=self.auth) as session:
            async with session.get(url) as response:
                if response.status == 404:
                    raise PackageNotFoundError(package=name, url=url)
                response.raise_for_status()
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

        # # Dirty hack to make DepHell much faster.
        # # If releases contains wheel then PyPI can parse requirements from it,
        # # but hasn't found iany requirements. So, release has no requirements.
        # # UPD: it doesn't work for prompt_toolkit
        # for file_info in files_info:
        #     if file_info['packagetype'] == 'bdist_wheel':
        #         return ()

        from ...converters import SDistConverter, WheelConverter

        sdist = SDistConverter()
        wheel = WheelConverter()
        rules = (
            (wheel, lambda info: info['packagetype'] == 'bdist_wheel'),
            (sdist, lambda info: info['packagetype'] == 'sdist'),
            (wheel, lambda info: info['filename'].endswith('.whl')),
            (sdist, lambda info: info['filename'].endswith('.tar.gz')),
            (sdist, lambda info: info['filename'].endswith('.zip')),
        )

        for converter, checker in rules:
            for file_info in files_info:
                if not checker(file_info):
                    continue
                try:
                    return await self._download_and_parse(
                        url=file_info['url'],
                        converter=converter,
                    )
                except FileNotFoundError as e:
                    logger.warning(e.args[0])
        return ()

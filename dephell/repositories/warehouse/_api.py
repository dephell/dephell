# built-in
import asyncio
from logging import getLogger
from typing import Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import urlparse, urljoin
from xmlrpc.client import ServerProxy

# external
import attr
import requests
from aiohttp import ClientSession
from dephell_licenses import License, licenses
from packaging.requirements import Requirement

# app
from ...cache import JSONCache, TextCache
from ...config import config
from ...exceptions import PackageNotFoundError, InvalidFieldsError
from ...models.author import Author
from ...models.release import Release
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
class WarehouseAPIRepo(WarehouseBaseRepo):
    name = attr.ib(default='pypi')
    url = attr.ib(type=str, factory=lambda: config['warehouse'], converter=_process_url)
    prereleases = attr.ib(type=bool, factory=lambda: config['prereleases'])  # allow prereleases

    propagate = True
    hash = None
    link = None

    @property
    def pretty_url(self):
        parsed = urlparse(self.url)
        path = '/simple/' if parsed.path == '/pypi/' else parsed.path
        return parsed.scheme + '://' + parsed.hostname + path

    def get_releases(self, dep) -> tuple:
        # retrieve data
        cache = JSONCache(
            urlparse(self.url).hostname, 'releases', dep.base_name,
            ttl=config['cache']['ttl'],
        )
        data = cache.load()
        if data is None:
            url = '{url}{name}/json'.format(url=self.url, name=dep.base_name)
            response = requests.get(url)
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
        if not release and prereleases:
            releases = prereleases

        releases.sort(reverse=True)
        return tuple(releases)

    async def get_dependencies(self, name: str, version: str,
                               extra: Optional[str] = None) -> Tuple[Requirement, ...]:
        cache = TextCache(urlparse(self.url).hostname, 'deps', name, str(version))
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
        url = urljoin(self.url, name, version, 'json')
        async with ClientSession() as session:
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
            (wheel, lambda info: info['url'].endswith('.whl')),
            (sdist, lambda info: info['url'].endswith('.tar.gz')),
            (sdist, lambda info: info['url'].endswith('.zip')),
        )

        for converer, checker in rules:
            for file_info in files_info:
                if not checker(file_info):
                    continue
                try:
                    return await self._download_and_parse(
                        url=file_info['url'],
                        converter=converer,
                    )
                except FileNotFoundError as e:
                    logger.warning(e.args[0])
        return ()

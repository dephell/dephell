# built-in
import asyncio
import re
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import urlparse
from xmlrpc.client import ServerProxy

# external
import attr
import requests
from aiohttp import ClientSession
from dephell_licenses import License, licenses
from dephell_markers import Markers
from packaging.requirements import InvalidRequirement, Requirement

# app
from ..cache import JSONCache, TextCache
from ..config import config
from ..models.author import Author
from ..models.release import Release
from .base import Interface


try:
    import aiofiles
except ImportError:
    aiofiles = None


logger = getLogger('dephell.repositories')
rex_token = re.compile(r'^((?P<field>[a-z_]+)\:)?(?P<value>.+)$')
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
class WareHouseRepo(Interface):
    name = attr.ib(default='pypi')
    url = attr.ib(type=str, factory=lambda: config['warehouse'], converter=_process_url)
    prereleases = attr.ib(type=bool, factory=lambda: config['prereleases'])  # allow prereleases

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
            try:
                req = Requirement(dep)
            except InvalidRequirement as e:
                msg = 'cannot parse requirement: {} from {} {}'
                try:
                    # try to parse with dropped out markers
                    req = Requirement(dep.split(';')[0])
                except InvalidRequirement:
                    raise ValueError(msg.format(dep, name, version)) from e
                else:
                    msg = 'cannot parse requirement: "{}" from {} {}'
                    logger.warning(msg.format(dep, name, version))

            try:
                dep_extra = req.marker and Markers(req.marker).extra
            except ValueError:  # unsupported operation for version marker python_version: in
                dep_extra = None

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

    def search(self, query: Iterable[str]) -> List[Dict[str, str]]:
        fields = dict()
        for token in query:
            group = rex_token.fullmatch(token).groupdict()
            fields[group['field'] or 'name'] = group['value']
        logger.debug('search on PyPI', extra=dict(query=fields))
        invalid_fields = set(fields) - _fields
        if invalid_fields:
            raise ValueError('Invalid fields: {}'.format(', '.join(invalid_fields)))

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

        # # Dirty hack to make DepHell much faster.
        # # If releases contains wheel then PyPI can parse requirements from it,
        # # but hasn't found iany requirements. So, release has no requirements.
        # # UPD: it doesn't work for prompt_toolkit
        # for file_info in files_info:
        #     if file_info['packagetype'] == 'bdist_wheel':
        #         return ()

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
                    try:
                        return await self._download_and_parse(url=file_info['url'], converter=converer)
                    except FileNotFoundError as e:
                        logger.warning(e.args[0])
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

                    # download file
                    if aiofiles is not None:
                        async with aiofiles.open(str(path), mode='wb') as stream:
                            while True:
                                chunk = await response.content.read(1024)
                                if not chunk:
                                    break
                                await stream.write(chunk)
                    else:
                        with path.open(mode='wb') as stream:
                            while True:
                                chunk = await response.content.read(1024)
                                if not chunk:
                                    break
                                stream.write(chunk)

            # load and make separated dep for every env
            root = converter.load(path)
            deps = []
            for dep in root.dependencies:
                for env in dep.envs.copy():
                    dep.envs = {env}
                    deps.append(str(dep))
            return tuple(deps)

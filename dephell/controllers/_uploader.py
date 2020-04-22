# built-in
import hashlib
import subprocess
from io import BytesIO
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

# external
import attr

# app
from ..cached_property import cached_property
from ..constants import DEFAULT_UPLOAD, TEST_UPLOAD
from ..networking import requests_session


BOUNDARY = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'


@attr.s()
class Uploader:
    url = attr.ib(type=str, default=DEFAULT_UPLOAD)
    auth = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.url = self._fix_url(url=self.url)

    @cached_property
    def hostname(self) -> str:
        return urlparse(self.url).hostname

    @staticmethod
    def _fix_url(url: str) -> str:
        if url == 'test':
            return TEST_UPLOAD
        if '://' not in url:
            url = 'https://' + url
        parsed = urlparse(url)
        if parsed.hostname in ('pypi.python.org', 'pypi.org'):
            return DEFAULT_UPLOAD
        if parsed.hostname in ('testpypi.python.org', 'test.pypi.org'):
            return TEST_UPLOAD
        return url

    @staticmethod
    def _get_hashes(path: Path) -> Dict[str, str]:
        sha256_manager = hashlib.sha256()
        md5_manager = hashlib.md5()
        if hasattr(hashlib, 'blake2b'):
            blake2_manager = hashlib.blake2b(digest_size=32)
        else:
            blake2_manager = None
        with path.open('rb') as stream:
            while True:
                data = stream.read(65536)
                if not data:
                    break
                sha256_manager.update(data)
                md5_manager.update(data)
                if blake2_manager:
                    blake2_manager.update(data)
        return dict(
            md5_digest=md5_manager.hexdigest(),
            sha256_digest=sha256_manager.hexdigest(),
            blake2_256_digest=blake2_manager.hexdigest(),
        )

    @classmethod
    def _get_file_info(cls, path: Path) -> dict:
        result = dict()

        # file type and python version
        if path.suffix == '.whl':
            result['filetype'] = 'bdist_wheel'
            result['pyversion'] = 'py3'
        elif path.suffix == '.gz':
            result['filetype'] = 'sdist'
            result['pyversion'] = 'source'
        else:
            raise TypeError('invalid extension: *{}'.format(path.suffix))

        # gpg signature
        sign_path = path.with_suffix(path.suffix + '.asc')
        if sign_path.exists():
            result['gpg_signature'] = sign_path.read_bytes()

        return result

    @classmethod
    def _get_metadata(cls, root) -> dict:
        meta = dict(
            # defaults that goes as-is on API
            comment=None,
            metadata_version='2.1',
            platform=None,
            supported_platform=[],
            provides_dist=[],
            requires_external=[],
            obsoletes_dist=[],
            provides=[],
            requires=[],
            obsoletes=[],

            # defaults that can be changed below
            project_urls=[],
            license=None,
            description=None,
            description_content_type='text/plain',

            name=root.name,
            version=root.version,
            summary=root.description or None,
            keywords=','.join(root.keywords) or None,
            classifiers=list(root.classifiers) or None,
        )

        if root.readme:
            meta['description_content_type'] = root.readme.content_type
            meta['description'] = root.readme.path.read_text()
        elif root.description:
            meta['description'] = root.description

        if root.license:
            meta['license'] = root.license

        if root.authors:
            author = root.authors[0]
            meta['author'] = author.name
            if author.mail:
                meta['author_email'] = author.mail
        if len(root.authors) > 1:
            author = root.authors[1]
            meta['maintainer'] = author.name
            if author.mail:
                meta['maintainer_email'] = author.mail

        for key, url in root.links.items():
            key = key[0].upper() + key[1:]
            meta['project_urls'].append('{}, {}'.format(key, url))

        if root.python:
            meta['requires_python'] = str(root.python.peppify())

        return meta

    @staticmethod
    def _get_reqs_info(reqs: list) -> dict:
        from ..converters import EggInfoConverter

        extras = set()
        for req in reqs:
            extras.update(req.main_envs)  # all envs (including dev and excluding main)

        reqs_result = []
        converter = EggInfoConverter()
        for req in reqs:
            reqs_result.append(converter._format_req(req=req, with_envs=True))
        return dict(
            provides_extras=sorted(extras),
            requires_dist=reqs_result,
        )

    @staticmethod
    def _dict_to_list(data: dict) -> list:
        result = []
        for key, value in data.items():
            if isinstance(value, (list, tuple)):
                for item in value:
                    result.append((key, item))
                continue
            result.append((key, value))
        return result

    @staticmethod
    def _make_body(data: list) -> bytes:
        sep_boundary = b'\r\n--' + BOUNDARY.encode('ascii')
        end_boundary = sep_boundary + b'--\r\n'
        body = BytesIO()
        for key, value in data:
            title = '\r\nContent-Disposition: form-data; name="{}"'.format(key)
            if type(value) is tuple:
                title += '; filename="{}"'.format(value[0])
                value = value[1]
            else:
                value = str(value).encode('utf-8')
            body.write(sep_boundary)
            body.write(title.encode('utf-8'))
            body.write(b'\r\n\r\n')
            body.write(value)
        body.write(end_boundary)
        return body.getvalue()

    @staticmethod
    def sign(path: Path, identity: str) -> bool:
        cmd = ['gpg', '--detach-sign']
        if identity:
            cmd.extend(['--local-user', identity])
        cmd.extend(['-a', str(path)])
        result = subprocess.run(cmd)
        return result.returncode == 0

    def upload(self, path: Path, root, reqs) -> None:
        data = {
            ':action': 'file_upload',
            'protocol_version': '1',
        }
        data.update(self._get_hashes(path=path))
        data.update(self._get_file_info(path=path))
        data.update(self._get_metadata(root=root))
        data.update(self._get_reqs_info(reqs=reqs))
        data = self._dict_to_list(data=data)
        data.append(('content', (path.name, path.read_bytes())))
        body = self._make_body(data=data)

        headers = {
            'Content-type': 'multipart/form-data; boundary=' + BOUNDARY,
            'Content-length': str(len(body)),
        }

        with requests_session(auth=self.auth) as session:
            response = session.post(
                url=self.url,
                data=body,
                allow_redirects=False,
                headers=headers,
            )
            response.raise_for_status()

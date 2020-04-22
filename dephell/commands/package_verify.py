# built-in
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory

# app
from ..actions import get_package, make_json
from ..config import builders
from ..imports import lazy_import
from ..networking import requests_session
from .base import BaseCommand


gnupg = lazy_import('gnupg', package='python-gnupg')
DEFAULT_KEYSERVER = 'pgp.mit.edu'


class PackageVerifyCommand(BaseCommand):
    """Verify GPG signature for a release from PyPI.org.
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', help='package name and version to validate')
        return parser

    def __call__(self) -> bool:
        dep = get_package(self.args.name, repo=self.config.get('repo'))
        releases = dep.repo.get_releases(dep)
        if not releases:
            self.logger.error('cannot find releases for the package')
            return False
        releases = dep.constraint.filter(releases=releases)
        if not releases:
            self.logger.error('cannot find releases for the constraint')
            return False
        release = sorted(releases, reverse=True)[0]
        gpg = gnupg.GPG()
        return self._verify_release(release=release, gpg=gpg)

    def _verify_release(self, release, gpg) -> bool:
        if not release.urls:
            self.logger.error('no urls found for release', extra=dict(
                version=str(release.version),
            ))
            return False

        verified = False
        all_valid = True
        with TemporaryDirectory() as root_path:
            for url in release.urls:
                sign_path = Path(root_path) / 'archive.bin.asc'
                with requests_session() as session:
                    response = session.get(url + '.asc')
                    if response.status_code == 404:
                        self.logger.debug('no signature found', extra=dict(url=url))
                        continue
                    sign_path.write_bytes(response.content)

                self.logger.info('getting release file...', extra=dict(url=url))
                with requests_session() as session:
                    response = session.get(url)
                    if response.status_code == 404:
                        self.logger.debug('no signature found', extra=dict(url=url))
                        continue
                    data = response.content

                info = self._verify_data(gpg=gpg, sign_path=sign_path, data=data)
                verified = True
                if not info:
                    return False
                if info['status'] != 'signature valid':
                    all_valid = False
                info['release'] = str(release.version)
                info['name'] = url.rsplit('/', maxsplit=1)[-1]
                print(make_json(
                    data=info,
                    key=self.config.get('filter'),
                    colors=not self.config['nocolors'],
                    table=self.config['table'],
                ))
        if not verified:
            self.logger.error('no signed files found')
            return False
        return all_valid

    def _verify_data(self, gpg, sign_path: Path, data: bytes, retry: bool = True):
        verif = gpg.verify_data(str(sign_path), data)
        result = dict(
            created=verif.creation_date,
            fingerprint=verif.fingerprint,
            key_id=verif.key_id,
            status=verif.status,
            username=verif.username,
        )

        if verif.status == 'no public key' and retry:
            # try to import keys and verify again
            self.logger.debug('searching the key...', extra=dict(key_id=verif.key_id))
            keys = gpg.search_keys(query=verif.key_id, keyserver=DEFAULT_KEYSERVER)
            if len(keys) != 1:
                self.logger.debug('cannot find the key', extra=dict(
                    count=len(keys),
                    key_id=verif.key_id,
                ))
                return result
            gpg.recv_keys(DEFAULT_KEYSERVER, keys[0]['keyid'])
            return self._verify_data(gpg=gpg, sign_path=sign_path, data=data, retry=False)

        return result

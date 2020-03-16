# built-in
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Optional

# app
from ..config import builders
from ..controllers import Uploader
from ..converters import CONVERTERS
from ..models import Auth, Requirement
from ..repositories import WarehouseAPIRepo
from .base import BaseCommand


class ProjectUploadCommand(BaseCommand):
    """Upload project dist archives on pypi.org (or somewhere else).
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_from(parser)

        group = parser.add_argument_group('Release upload')
        group.add_argument('--upload-sign', help='sign packages with GPG')
        group.add_argument('--upload-identity', help='use name as the key to sign with')
        group.add_argument('--upload-url', help='use name as the key to sign with')

        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        if 'from' not in self.config:
            self.logger.error('`--from` is required for this command')
            return False

        uploader = Uploader(url=self.config['upload']['url'])
        # auth
        for cred in self.config['auth']:
            if cred['hostname'] == uploader.hostname:
                uploader.auth = Auth(**cred)
        if uploader.auth is None:
            self.logger.error('no credentials found', extra=dict(hostname=uploader.hostname))
            return False

        # metainfo
        loader = CONVERTERS[self.config['from']['format']]
        loader = loader.copy(project_path=Path(self.config['project']))
        resolver = loader.load_resolver(path=self.config['from']['path'])
        root = resolver.graph.metainfo
        reqs = Requirement.from_graph(resolver.graph, lock=False)
        self.logger.info('uploading release', extra=dict(
            release_name=root.raw_name,
            release_version=root.version,
            upload_url=uploader.url,
        ))

        # get release info to check uploaded files
        release = None
        if uploader.hostname in {'pypi.org', 'test.pypi.org'}:
            repo = WarehouseAPIRepo(name='pypi', url='https://{}/'.format(uploader.hostname))
            releases = repo.get_releases(dep=root)
            if not releases:
                self.logger.debug('cannot find releases', extra=dict(
                    release_name=root.name,
                ))
            releases = [r for r in releases if str(r.version) == root.version]
            if len(releases) == 1:
                release = releases[0]
            else:
                self.logger.debug('cannot find release', extra=dict(
                    release_name=root.name,
                    version=root.version,
                    count=len(releases),
                ))

        # files to upload
        paths = self._get_paths(loader=loader, root=root)
        if not paths:
            self.logger.error('no release files found')
            return False

        # do upload
        uploaded = False
        for path in paths:
            url = self._uploaded(release=release, path=path)
            if url:
                self.logger.info('dist already uploaded', extra=dict(path=str(path), url=url))
                continue
            uploaded = True
            self.logger.info('uploading dist...', extra=dict(path=str(path)))
            if self.config['upload']['sign']:
                uploader.sign(
                    path=path,
                    identity=self.config['upload'].get('identity'),
                )
            uploader.upload(path=path, root=root, reqs=reqs)

        if not uploaded:
            self.logger.warning('all dists already uploaded, nothing to do.')
            return True

        # show release url
        if uploader.hostname in {'pypi.org', 'test.pypi.org'}:
            url = 'https://{h}/project/{n}/{v}/'.format(
                h=uploader.hostname,
                n=root.name,
                v=root.version,
            )
            self.logger.info('release uploaded', extra=dict(url=url))
        else:
            self.logger.info('release uploaded')
        return True

    def _get_paths(self, loader, root) -> List[Path]:
        if self.config['from']['path'].endswith(('.tar.gz', '.whl')):
            return [Path(self.config['from']['path'])]

        # check dist dir if from-format is sdist or wheel
        fmt = self.config['from']['format']
        if fmt in {'sdist', 'wheel'}:
            path = Path(self.config['from']['path'])
            if path.is_dir():
                if fmt == 'sdist':
                    dists = list(path.glob('*.tar.gz'))
                else:
                    dists = list(path.glob('*.whl'))
                if len(dists) == 1:
                    return dists
                # TODO: can we infer the name without knowing metadata?
                raise FileNotFoundError('please, specify full path to the file')
            raise IOError('invalid file extension: {}'.format(path.suffix))

        path = Path(self.config['project']) / 'dist'
        if not path.is_dir():
            raise FileNotFoundError('cannot find ./dist/ dir')

        # look for one-release archives in the dir
        sdists = list(path.glob('*.tar.gz'))
        wheels = list(path.glob('*.whl'))
        if len(sdists) == 1 and len(wheels) == 1:
            return sdists + wheels

        result = []

        # find sdist
        file_name = '{name}-{version}.tar.gz'.format(
            name=root.raw_name,
            version=root.pep_version,
        )
        if (path / file_name).exists():
            result.append(path / file_name)

        # find wheel
        glob = '{name}-{version}-py*-*-*.whl'.format(
            name=root.raw_name.replace('-', '_'),
            version=root.pep_version,
        )
        result.extend(list(path.glob(glob)))

        return result

    def _uploaded(self, release, path: Path) -> Optional[str]:
        if release is None:
            return None
        for url in release.urls:
            if url.rsplit('/', maxsplit=1)[-1] == path.name:
                return url
        return None

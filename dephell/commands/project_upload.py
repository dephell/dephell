# built-in
from argparse import ArgumentParser
from pathlib import Path
from typing import List

# app
from ..config import builders
from ..controllers import Uploader
from ..converters import CONVERTERS
from ..models import Auth, Requirement
from .base import BaseCommand


class ProjectBuildCommand(BaseCommand):
    """Upload project dist archives on pypi.org (or somewhere else).
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        uploader = Uploader()
        for cred in self.config['auth']:
            if cred['hostname'] == uploader.hostname:
                uploader.auth = Auth(**cred)

        loader = CONVERTERS[self.config['from']['format']]
        loader = loader.copy(project_path=Path(self.config['project']))
        resolver = loader.load_resolver(path=self.config['from']['path'])
        root = resolver.graph.metainfo
        reqs = Requirement.from_graph(resolver.graph, lock=False)

        paths = self._get_paths(loader=loader, root=root)
        for path in paths:
            if ...:
                uploader.sign(path=path, identity=...)
            uploader.upload(path=path, root=root, reqs=reqs)
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

        if not result:
            raise LookupError('cannot find sdist or wheel for the release')
        return result

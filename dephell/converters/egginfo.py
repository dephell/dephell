# built-in
from email.parser import Parser
from pathlib import Path
from itertools import chain

# external
from packaging.requirements import Requirement as PackagingRequirement

# app
from ..models import Dependency, RootDependency
from .base import BaseConverter
from ..archive import ArchivePath


class EggInfoConverter(BaseConverter):
    """
    PEP-314
    """
    lock = False

    def load(self, path) -> RootDependency:
        path = Path(str(path))
        if path.is_dir():
            # load from *.egg-info dir
            if path.name.endswith('.egg-info'):
                return self._load_dir(path)
            # find *.egg-info in current dir
            paths = list(path.glob('*/*.egg-info'))
            return self._load_dir(*paths)

        # load from archive
        if path.suffix in ('.zip', '.gz', '.tar'):
            archive = ArchivePath(path)
            paths = list(archive.glob('*/*.egg-info'))
            return self._load_dir(*paths)

        # load from file (requires.txt or PKG-INFO)
        with path.open('r') as stream:
            return self.loads(stream.read())

    def loads(self, content: str) -> RootDependency:
        if 'Name: ' in content:
            return self._parse_info(content)
        else:
            return self._parse_requires(content)

    def dumps(self, reqs, content=None) -> str:
        # distutils.dist.DistributionMetadata.write_pkg_file
        content = []
        content.append(('Metadata-Version', '1.1'))
        # TODO: get project info
        content.append(('Name', 'UNKNOWN'))
        content.append(('Version', '0.0.0'))

        for req in reqs:
            content.append(('Requires', self._format_req(req=req)))
        return '\n'.join(map(': '.join, content))

    # helpers

    def _load_dir(self, *paths):
        if not paths:
            raise FileNotFoundError('cannot find egg-info')
        # maybe it's possible, so we will have to process it
        if len(paths) > 1:
            raise FileExistsError('too many egg-info')
        path = paths[0]

        with (path / 'PKG-INFO').open('r') as stream:
            content = stream.read()
        root = self._parse_info(content)
        path = path / 'requires.txt'
        if not root.dependencies:
            with path.open('r') as stream:
                content = stream.read()
            root = self._parse_requires(content, root=root)
        return root

    @staticmethod
    def _parse_info(content: str, root=None) -> RootDependency:
        info = Parser().parsestr(content)
        root = RootDependency(name=info.get('Name').strip())
        deps = []
        reqs = chain(
            info.get_all('Requires', []),
            info.get_all('Requires-Dist', []),
        )
        for req in reqs:
            req = PackagingRequirement(req)
            deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

    def _parse_requires(self, content: str, root=None) -> RootDependency:
        if root is None:
            root = RootDependency(name=self._get_name(content=content))
        deps = []
        for req in content.split():
            req = PackagingRequirement(req)
            deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

    @staticmethod
    def _format_req(req):
        line = req.name
        if req.extras:
            line += '[{extras}]'.format(extras=','.join(req.extras))
        if req.version:
            line += req.version
        if req.markers:
            line += '; ' + req.markers
        return line

# built-in
from pathlib import Path
from types import SimpleNamespace
from typing import Optional
from urllib.parse import urlparse

# external
from dephell_links import DirLink
from pip._internal.download import PipSession
from pip._internal.index import PackageFinder
from pip._internal.req import parse_requirements

# app
from ..config import config
from ..controllers import DependencyMaker, RepositoriesRegistry
from ..models import RootDependency
from .base import BaseConverter


class PIPConverter(BaseConverter):
    sep = ' \\\n  '

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if isinstance(path, str):
            path = Path(path)

        if path.name == 'requirements.txt':
            if path.with_name('requirements.in').exists():
                return (self.lock is True)
            if path.with_name('requirements.lock').exists():
                return (self.lock is False)
            return True

        if self.lock:
            return (path.name == 'requirements.lock')
        else:
            return (path.name == 'requirements.in')

    def __init__(self, lock):
        self.lock = lock

    def load(self, path) -> RootDependency:
        deps = []
        root = RootDependency()

        warehouse_urls = []
        for url in config['warehouse']:
            host = urlparse(url).hostname
            if host in ('pypi.org', 'pypi.python.org', 'test.pypi.org'):
                warehouse_urls.append('https://{}/simple'.format(host))

        finder = PackageFinder(
            find_links=[],
            index_urls=warehouse_urls,
            session=PipSession(),
        )
        # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/constructors.py
        reqs = parse_requirements(
            filename=str(path),
            session=PipSession(),
            finder=finder,
        )

        for req in reqs:
            # https://github.com/pypa/pip/blob/master/src/pip/_internal/req/req_install.py
            if req.req is None:
                req.req = SimpleNamespace(
                    name=req.link.url.split('/')[-1],
                    specifier='*',
                    marker=None,
                    extras=None,
                )
            deps.extend(DependencyMaker.from_requirement(
                source=root,
                req=req.req,
                url=req.link and req.link.url,
                editable=req.editable,
            ))

        # update repository
        if finder.index_urls:
            repo = RepositoriesRegistry()
            for url in finder.index_urls:
                repo.add_repo(url=url)
            for url in config['warehouse']:
                repo.add_repo(url=url)
            for dep in deps:
                if isinstance(dep.repo, RepositoriesRegistry):
                    dep.repo = repo

        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, project: Optional[RootDependency] = None,
              content: Optional[str] = None) -> str:
        lines = []

        # get repos urls
        urls = []
        names = set()
        for req in reqs:
            if not isinstance(req.dep.repo, RepositoriesRegistry):
                continue
            for repo in req.dep.repo.repos:
                if repo.name in names:
                    continue
                names.add(repo.name)
                urls.append(repo.pretty_url)
        # dump repos urls
        if urls:
            lines.append('-i ' + urls[0])
        for url in urls[1:]:
            lines.append('--extra-index-url ' + url)

        # disable hashes when dir-based deps are presented
        # https://github.com/dephell/dephell/issues/41
        with_hashes = not any(isinstance(req.dep.link, DirLink) for req in reqs)

        for req in reqs:
            lines.append(self._format_req(req=req, with_hashes=with_hashes))
        return '\n'.join(lines) + '\n'

    # https://github.com/pypa/packaging/blob/master/packaging/requirements.py
    # https://github.com/jazzband/pip-tools/blob/master/piptools/utils.py
    def _format_req(self, req, *, with_hashes: bool = True) -> str:
        line = ''
        if req.editable:
            line += '-e '
        if req.link is not None:
            req.link.name = req.name  # patch `#=egg` by right name
            line += req.link.long
        else:
            line += req.raw_name
        if req.extras:
            line += '[{extras}]'.format(extras=','.join(req.extras))
        if req.version:
            line += req.version
        if req.markers:
            line += '; ' + req.markers
        if with_hashes and req.hashes:
            for digest in req.hashes:
                # https://github.com/jazzband/pip-tools/blob/master/piptools/writer.py
                line += '{sep}--hash {hash}'.format(
                    sep=self.sep,
                    hash=digest,
                )
        if self.lock and req.sources:
            line += '{sep}# ^ from {sources}'.format(
                sep=self.sep,
                sources=', '.join(req.sources),
            )
        return line

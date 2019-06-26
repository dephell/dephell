# built-in
import re
import subprocess
from collections import OrderedDict
from datetime import datetime
from logging import getLogger
from pathlib import Path
from typing import Optional

# app
from ...cache import RequirementsCache
from ...config import config
from ...context_tools import chdir
from ...models.git_release import GitRelease
from ...models.release import Release
from ...cached_property import cached_property
from ..base import Interface
from .._local import LocalRepo


logger = getLogger(__name__)
rex_version = re.compile(r'(?:refs/tags/)?v?\.?\s*(.+)')


class GitRepo(Interface):
    _ready = False
    name = 'git'

    def __init__(self, link):
        self.link = link

    # PROPERTIES

    @cached_property
    def tags(self) -> OrderedDict:
        """
        From newest to oldest.
        tag -> time
        """
        self._setup()
        tags = self._call('tag')
        result = [(tag, self._get_rev_time(tag)) for tag in tags]
        # show-ref returns tags in alphabet order, so we have to sort tags ourselves.
        result.sort(key=lambda line: line[1], reverse=True)
        return OrderedDict(result)

    @cached_property
    def path(self):
        name = self.link.name
        host = self.link.server or 'localhost'
        author = self.link.author or 'anonimous'
        path = Path(config['cache']['path']) / 'git' / host / 'repo' / author / name
        return path

    @cached_property
    def metaversion(self):
        if self.link.rev:
            return self.get_nearest_version(self.link.rev)

    # PUBLIC METHODS

    def read_file(self, path):
        """
        IMPORTANT: it's danger method. It's allow you to read any file,
        even not in repository. Don't allow external calls for it.
        """
        if isinstance(path, str):
            path = Path(path)
        with chdir(self.path):
            with path.open('r') as stream:
                return stream.read()

    def get_releases(self, dep) -> tuple:
        releases = []
        # add tags to releases
        for tag, time in reversed(self.tags.items()):
            release = Release(
                raw_name=dep.raw_name,
                version=self._clean_tag(tag),
                time=time,
            )
            releases.append(release)

        # add current revision to releases
        if self.link.rev:
            release = GitRelease(
                raw_name=dep.raw_name,
                version=self.metaversion,
                commit=self.link.rev,
                time=self._get_rev_time(self.link.rev),
            )
            releases.append(release)
        return tuple(releases)

    async def get_dependencies(self, name: str, version, extra: Optional[str] = None) -> tuple:
        # get from cache
        host = self.link.server or 'localhost'
        author = self.link.author or 'anonimous'
        cache = RequirementsCache('git', host, 'deps', author, name, str(version))
        deps = cache.load()
        if deps:
            if extra:
                deps = tuple(dep for dep in deps if extra in dep.envs)
            return deps

        # load deps
        self._setup()
        self._call('checkout', self._version_to_rev(version))
        root = LocalRepo(path=self.path).get_root(name=name, version=version)
        cache.dump(root=root)

        # filter extras
        deps = root.dependencies
        if extra:
            deps = tuple(dep for dep in deps if extra in dep.envs)
        return tuple(deps)

    def get_nearest_version(self, ref: str):
        # get version in that this commit has included
        result = self._call('describe', '--contains', ref)[0]
        if '~' in result:
            result = result.split('~')[0].split('^')[0]
            return self._clean_tag(result)

        # if this commit isn't released yet than return latest release
        tag = next(iter(self.tags))
        return self._clean_tag(tag)

    # PRIVATE METHODS

    def _call(self, *args, path=None) -> tuple:
        if path is None:
            path = self.path
        with chdir(path):
            result = subprocess.run(
                [self.name] + list(args),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        if result.returncode != 0:
            logger.error(result.stderr)
        return tuple(result.stdout.decode().strip().split('\n'))

    def _get_rev_time(self, rev: str) -> datetime:
        data = self._call('show', '-s', r'--format="%cI"', rev)
        date = data[-1].strip().strip('"')  # '2018-09-03T13:51:53+03:00'
        # Python 3.6 cannot parse timezone with `:`.
        date = date[:-3] + date[-2:]        # '2018-09-03T13:51:53+0300'
        return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')

    def _get_rev_hash(self, rev: str):
        data = self._call('show', '-s', r'--format="%H"', rev)
        return data[-1].strip().strip('"')

    @staticmethod
    def _clean_tag(tag):
        return rex_version.fullmatch(tag).groups()[0]

    def _version_to_rev(self, version) -> str:
        version = str(version)
        if version in self.tags:
            return version
        for tag in self.tags:
            if tag.endswith(version):
                chars = set(tag[:-len(version)])
                if not (chars - {'v', 'V', '.', ' '}):
                    return tag
        # TODO: look for version in setup.py and other places
        ...
        raise LookupError('cannot find tag for version ' + version)

    def _setup(self, *, force: bool = False) -> None:
        if self._ready and not force:
            return

        # clone or fetch
        if self.path.exists():
            if '.git' not in (subpath.name for subpath in self.path.iterdir()):
                raise FileNotFoundError('.git directory not found in project cache')
            self._call('fetch')
        else:
            self._call(
                'clone', self.link.short, self.path.name,
                path=self.path.parent,
            )

        if self.link.rev:
            self._call('checkout', self.link.rev)
        self._ready = True

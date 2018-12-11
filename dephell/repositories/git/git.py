# built-in
import re
import subprocess
from collections import OrderedDict
from pathlib import Path

# external
from cached_property import cached_property

# app
from ...config import config
from ...models.git_release import GitRelease
from ...models.release import Release
from ...utils import chdir
from ..base import Interface


try:
    from dateutil.parser import isoparse
except ImportError:
    from dateutil.parser import parse as isoparse


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
        commit_hash -> tag
        """
        self._setup()
        log = self._call('show-ref', '--tags')
        result = [line.split() for line in log]
        # show-ref returns tags in alphabet order, so we have to sort tags ourselves.
        result.sort(key=lambda line: self.commits[line[0]], reverse=True)
        return OrderedDict(result)

    @cached_property
    def commits(self) -> OrderedDict:
        """
        From newest to oldest.
        commit_hash -> time
        """
        self._setup()
        log = self._call('log', r'--format="%H %cI"')
        result = (line.replace('"', '').split() for line in log)
        return OrderedDict((rev, isoparse(time)) for rev, time in result)

    @cached_property
    def path(self):
        name = self.link.name
        path = Path(config['cache']) / self.name / name
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
        # rev -- commit hash (2d6989d9bcb7fe250a7e55d8e367ac1e0c7d7f55)
        # ref -- tag name (refs/tags/v0.1.0)
        for rev, ref in reversed(self.tags.items()):
            release = Release(
                raw_name=dep.raw_name,
                version=self._clean_tag(ref),
                time=self.commits[rev],
            )
            releases.append(release)

        # add current revision to releases
        if self.link.rev:
            release = GitRelease(
                raw_name=dep.raw_name,
                version=self.metaversion,
                commit=self.link.rev,
                time=self.commits[self.link.rev],
            )
            releases.append(release)
        return tuple(releases)

    async def get_dependencies(self, name: str, version: str) -> tuple:
        self._setup()
        self._call('checkout', str(version))
        path = self.path / 'setup.py'
        if not path.exists():
            return ()

        # sorry for that
        from ...converters import SetupPyConverter

        root = SetupPyConverter().load(path)
        return tuple(root.dependencies)

    def get_nearest_version(self, ref: str):
        # get version in that this commit has included
        result = self._call('describe', '--contains', ref)[0]
        if '~' in result:
            result = result.split('~')[0].split('^')[0]
            return self._clean_tag(result)

        # if this commit isn't released yet than return latest release
        tag = next(iter(self.tags.values()))
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
            print(result.stderr)
        return tuple(result.stdout.decode().strip().split('\n'))

    @staticmethod
    def _clean_tag(tag):
        return rex_version.fullmatch(tag).groups()[0]

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

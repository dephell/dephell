# built-in
import re
import subprocess
from pathlib import Path

# external
from cached_property import cached_property

# app
from ...constants import CACHE_DIR
from ...models.release import Release
from ...utils import chdir
from ..base import Interface


try:
    from dateutil.parser import isoparse
except ImportError:
    from dateutil.parser import parse as isoparse


rex_author = re.compile(r'$/([a-zA-Z_-])')


class GitRepo(Interface):
    _ready = False
    name = 'git'

    def __init__(self, link):
        self.link = link

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

    def _get_tags(self) -> tuple:
        log = self._call('show-ref', '--tags')
        return tuple(line.split() for line in log)

    def _get_commits(self) -> tuple:
        log = self._call('log', r'--format="%H %cI"')
        return tuple(line.replace('"', '').split() for line in log)

    @cached_property
    def path(self):
        name = self.link.name
        path = Path(CACHE_DIR) / self.name / name
        return path

    def _setup(self, *, force: bool=False) -> None:
        if self._ready and not force:
            return
        if not self.path.exists() or '.git' not in set(self.path.iterdir()):
            self._call(
                'clone', self.link.short, self.path.name,
                path=self.path.parent,
            )
        else:
            self._call('fetch')
        if self.link.rev:
            self._call('checkout', self.link.rev)
        self._ready = True

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
        self._setup()
        commits = dict(self._get_commits())

        # add tags to releases
        # rev -- commit hash (2d6989d9bcb7fe250a7e55d8e367ac1e0c7d7f55)
        # ref -- tag name (refs/tags/v0.1.0)
        for rev, ref in self._get_tags():
            release = Release(
                raw_name=dep.raw_name,
                version=ref.replace('refs/tags/', ''),
                time=isoparse(commits[rev]),
            )
            releases.append(release)

        # add current revision to releases
        if self.link.rev:
            release = Release(
                raw_name=dep.raw_name,
                version=self.link.rev,
                time=isoparse(commits[self.link.rev]),
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

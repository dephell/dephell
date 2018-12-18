# built-in
import re
from logging import getLogger
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

    async def get_dependencies(self, name: str, version: str) -> tuple:
        self._setup()
        self._call('checkout', str(version))
        path = self.path / 'setup.py'
        if not path.exists():
            return ()

        # sorry for that
        from ...converters import SetupPyConverter

        try:
            root = SetupPyConverter().load(path)
        except BaseException:
            logger.exception('cannot read setup.py')
            return ()
        return tuple(root.dependencies)

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
            print(result.stderr)
        return tuple(result.stdout.decode().strip().split('\n'))

    def _get_rev_time(self, rev: str):
        data = self._call('show', '-s', r'--format="%cI"', rev)
        return isoparse(data[-1].strip().strip('"'))

    def _get_rev_hash(self, rev: str):
        data = self._call('show', '-s', r'--format="%H"', rev)
        return data[-1].strip().strip('"')

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

import re
import subprocess
from pathlib import Path

from cached_property import cached_property

from ..base import BaseRepo
from ...constants import CACHE_DIR
from ...utils import chdir


rex_author = re.compile(r'$/([a-zA-Z_-])')


class GitRepo(BaseRepo):
    def __init__(self, link):
        self.link = link

    def _get_tags(self):
        with chdir(self.path):
            result = subprocess.call(['git', 'tag'])
            return result.stdout.decode().split()

    def _get_commits(self):
        with chdir(self.path):
            result = subprocess.call(['git', 'log', 'format', r'%H %cI'])
            return result.stdout.decode().split('\n')

    @cached_property
    def path(self):
        name = self.link.name
        path = Path(CACHE_DIR) / 'git' / name
        return path

    def _setup(self):
        if not self.path.exists():
            subprocess.call(['git', 'clone', self.link.short, str(self.path)])
        with chdir(self.path):
            subprocess.call(['git', 'checkout', self.link.rev])

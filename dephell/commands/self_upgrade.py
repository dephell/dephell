# built-in
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..context_tools import chdir
from ..package_manager import PackageManager
from .base import BaseCommand


class SelfUpgradeCommand(BaseCommand):
    """Upgrade DepHell to the latest version.
    """

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        path = Path(__file__).parent.parent.parent
        if (path / 'README.md').exists() and (path / '.git').exists():
            return self._upgrade_repo(path=path)
        return self._upgrade_package()

    def _upgrade_repo(self, path: Path) -> bool:
        with chdir(path):
            cmd = ['git', 'pull', 'origin', 'master']
            result = subprocess.run(cmd)
            return (result.returncode == 0)

    def _upgrade_package(self) -> bool:
        manager = PackageManager(executable=sys.executable)
        args = ['-U']
        if manager.is_global:
            args.append('--user')
        else:
            args.append('--upgrade-strategy=eager')
        code = manager.run('install', *args, 'dephell')
        return (code == 0)

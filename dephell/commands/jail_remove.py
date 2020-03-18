# built-in
import shutil
from argparse import ArgumentParser
from pathlib import Path

# external
from dephell_venvs import VEnvs
from packaging.utils import canonicalize_name

# app
from ..config import builders
from .base import BaseCommand


class JailRemoveCommand(BaseCommand):
    """Remove package isolated environment.
    """
    find_config = False

    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs='+', help='jails names to uninstall')
        return parser

    def __call__(self) -> bool:
        venvs = VEnvs(path=self.config['venv'])
        for name in self.args.name:
            name = canonicalize_name(name)
            venv = venvs.get_by_name(name)
            if not venv.exists():
                self.logger.error('jail does not exist', extra=dict(package=name))
                return False

            # remove symlinks on entrypoints
            self.logger.info('remove executables...')
            for entrypoint in venv.bin_path.iterdir():
                global_entrypoint = Path(self.config['bin']) / entrypoint.name
                if not global_entrypoint.exists():
                    continue
                if not global_entrypoint.resolve().samefile(entrypoint):
                    continue
                global_entrypoint.unlink()
                self.logger.info('removed', extra=dict(script=entrypoint.name))

            # remove venv
            shutil.rmtree(venv.path)
            self.logger.info('jail removed', extra=dict(package=name))

        return True

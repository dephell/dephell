# built-in
import shutil
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..venvs import VEnvs
from .base import BaseCommand


class JailRemoveCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell jail remove',
            description='Remove package isolated environment',
        )
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs='?')
        return parser

    def __call__(self) -> bool:
        name = self.args.name
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get_by_name(name)
        if not venv.exists():
            self.logger.error('jail does not exist', extra=dict(package=name))
            return False

        # remove symlinks on entrypoints
        self.logger.info('remove executables...')
        for entrypoint in venv.bin_path.iterdir():
            global_entrypoint = Path(self.config['bin']) / entrypoint.name
            if global_entrypoint.exists():
                if global_entrypoint.resolve().samefile(entrypoint):
                    global_entrypoint.unlink()
                    self.logger.info('removed', extra=dict(script=entrypoint.name))

        # remove venv
        shutil.rmtree(venv.path)
        self.logger.info('jail removed', extra=dict(package=name))
        return True

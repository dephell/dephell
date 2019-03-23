
# built-in
import shutil
from argparse import ArgumentParser

# app
from ..config import builders
from ..venvs import VEnvs
from .base import BaseCommand


class JailRemoveCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell jail remove',
            description='remove package isolated environment',
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
        shutil.rmtree(venv.path)
        self.logger.info('jail removed', extra=dict(package=name))
        return True

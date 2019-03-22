# built-in
from argparse import ArgumentParser
from pathlib import Path
from shutil import rmtree

# app
from ..config import builders
from ..venvs import VEnvs
from .base import BaseCommand


class DestroyCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell create',
            description='Destroy virtual environment for current project.',
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        if not venv.exists():
            self.logger.warning('venv does not exists')
            return False
        rmtree(str(venv.path))
        self.logger.info('venv removed')
        return True

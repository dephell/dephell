# built-in
from argparse import ArgumentParser
from pathlib import Path

# external
from dephell_venvs import VEnvs

# app
from ..config import builders
from .base import BaseCommand


class VenvDestroyCommand(BaseCommand):
    """Destroy virtual environment for current project.

    https://dephell.readthedocs.io/en/latest/cmd-venv-destroy.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell venv destroy',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        if not venv.exists():
            self.logger.error('venv does not exist')
            return False
        venv.destroy()
        self.logger.info('venv removed')
        return True

from argparse import ArgumentParser
from pathlib import Path

# app
from .base import BaseCommand
from ..config import builders
from ..venvs import VEnvs
from ..shells import Shells
from ..pythons import Pythons


class ShellCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell config',
            description='Activate virtual environment for current project.',
        )
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self):
        venvs = VEnvs(path=self.config['venv']['path'])
        venv = venvs.get(Path(self.config['project']))
        if not venv.exists():
            self.good('Creating venv for project...')
            python = Pythons().get_best(self.config['venv'].get('python'))
            self.good('Choosen python: {}'.format(python.version))
            venv.create(python_path=python.path)

        shells = Shells(bin_path=venv.bin_path)
        shells.run()
        return True

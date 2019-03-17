from argparse import ArgumentParser
from pathlib import Path

# app
from .base import BaseCommand
from ..config import builders
from ..venvs import VEnvs
from ..shells import Shells
from ..pythons import Pythons, Python
from ..converters import CONVERTERS


class ShellCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell shell',
            description='Activate virtual environment for current project.',
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def _get_python(self) -> Python:
        pythons = Pythons()

        # defined in config
        python = self.config['venv'].get('python')
        if python:
            return pythons.get_best(python)

        # defined in dependency file
        loader = CONVERTERS[self.config['from']['format']]
        root = loader.load(path=self.config['from']['path'])
        if root.python:
            return pythons.get_by_spec(root.python)

        return pythons.current

    def __call__(self):
        venvs = VEnvs(path=self.config['venv']['path'])
        venv = venvs.get(Path(self.config['project']))
        if not venv.exists():
            self.good('Creating venv for project...')
            python = self._get_python()
            self.good('Choosen python: {}'.format(python.version))
            venv.create(python_path=python.path)

        shells = Shells(bin_path=venv.bin_path)
        shells.run()
        return True

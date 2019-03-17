from argparse import ArgumentParser
from pathlib import Path

# app
from .base import BaseCommand
from ..config import builders
from ..venvs import VEnvs
from ..shells import Shells


class InfoCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell info',
            description='Show virtual environment information for current project.',
        )
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('key', nargs='?')
        return parser

    def __call__(self):
        venvs = VEnvs(path=self.config['venv']['path'])
        venv = venvs.get(Path(self.config['project']))
        shells = Shells(bin_path=venv.bin_path)
        data = dict(
            bin=str(venv.bin_path),
            python=str(venv.python_path),
            exists=venv.exists(),
            activate=str(venv.bin_path / shells.current.activate),
            project=self.config['project'],
        )
        print(self.get_value(data=data, key=self.args.key))

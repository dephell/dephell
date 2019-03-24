# built-in
import subprocess
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..venvs import VEnvs
from .base import BaseCommand


class RunCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell run',
            description='Run command inside venv',
        )
        builders.build_config(parser)
        builders.build_api(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs='+', help='command to run')
        return parser

    def __call__(self) -> bool:
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        if not venv.exists():
            self.logger.error('venv does not exists', extra=dict(project=self.config['project']))
            return False

        executable = venv.bin_path / self.args.name[0]
        if not executable.exists():
            self.logger.error('executable does not found in venv', extra=dict(
                executable=executable.name,
            ))
            return False

        result = subprocess.run([str(executable)] + self.args.name[1:])
        return not result.returncode

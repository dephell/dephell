# built-in
import subprocess
import shlex
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
        parser.add_argument('name', nargs='*', help='command to run')
        return parser

    def __call__(self) -> bool:
        command = self.args.name
        if not command:
            command = self.config.get('command')
            if not command:
                self.logger.error('command required')
                return False
        if isinstance(command, str):
            command = shlex.split(command)

        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        if not venv.exists():
            self.logger.error('venv does not exists', extra=dict(
                project=self.config['project'],
                env=self.config.env,
            ))
            return False

        executable = venv.bin_path / command[0]
        if not executable.exists():
            self.logger.error('executable does not found in venv', extra=dict(
                executable=command[0],
            ))
            return False

        result = subprocess.run([str(executable)] + command[1:])
        return not result.returncode

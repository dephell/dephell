# built-in
import os
import shlex
import subprocess
from argparse import REMAINDER, ArgumentParser
from pathlib import Path

# external
from dephell_venvs import VEnvs

# app
from ..actions import get_python, install_dep, read_dotenv
from ..config import builders
from ..context_tools import override_env_vars
from .base import BaseCommand


class VenvRunCommand(BaseCommand):
    """Run command in the project virtual environment
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_api(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='command to run')
        return parser

    def __call__(self) -> bool:
        # get command
        command = self.args.name
        if not command:
            command = self.config.get('command')
            if not command:
                self.logger.error('command required')
                return False
        if isinstance(command, str):
            command = shlex.split(command)

        # get and make venv
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        if not venv.exists():
            self.logger.warning('venv does not exist, creating...', extra=dict(
                project=self.config['project'],
                env=self.config.env,
                path=str(venv.path),
            ))
            python = get_python(self.config)
            self.logger.debug('choosen python', extra=dict(version=python.version))
            venv.create(python_path=python.path)
            self.logger.info('venv created', extra=dict(path=venv.path))

        # install executable
        executable = venv.bin_path / command[0]
        if not executable.exists():
            self.logger.warning('executable is not found in venv, trying to install...', extra=dict(
                executable=command[0],
            ))
            result = install_dep(
                name=command[0],
                python_path=venv.python_path,
                logger=self.logger,
                silent=self.config['silent'],
            )
            if not result:
                return False
        if not executable.exists():
            self.logger.error('package installed, but executable is not found')
            return False

        # get env vars
        env_vars = os.environ.copy()
        if 'vars' in self.config:
            env_vars.update(self.config['vars'])
        env_vars = read_dotenv(
            path=Path(self.config['dotenv']),
            env_vars=env_vars,
        )

        # run
        self.logger.info('running...', extra=dict(command=command))
        with override_env_vars(env_vars):
            result = subprocess.run([str(executable)] + command[1:])
        if result.returncode != 0:
            self.logger.error('command failed', extra=dict(code=result.returncode))
            return False

        self.logger.info('command successfully completed')
        return True

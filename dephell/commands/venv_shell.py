# built-in
import os
from argparse import ArgumentParser
from pathlib import Path

# external
from dephell_shells import Shells
from dephell_venvs import VEnvs

# app
from ..actions import get_python, read_dotenv
from ..config import builders
from ..context_tools import override_env_vars
from .base import BaseCommand


class VenvShellCommand(BaseCommand):
    """Activate virtual environment for current project.

    https://dephell.readthedocs.io/cmd-venv-shell.html
    """

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell venv shell',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        # get and create venv
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        if not venv.exists():
            self.logger.info('Creating venv for project...')
            python = get_python(self.config)
            self.logger.debug('choosen python', extra=dict(version=python.version))
            venv.create(python_path=python.path)

        # get env vars
        env_vars = os.environ.copy()
        if 'vars' in self.config:
            env_vars.update(self.config['vars'])
        env_vars = read_dotenv(
            path=Path(self.config['dotenv']),
            env_vars=env_vars,
        )

        shells = Shells(bin_path=venv.bin_path)
        with override_env_vars(env_vars):
            shells.run()
        self.logger.info('shell closed')
        return True

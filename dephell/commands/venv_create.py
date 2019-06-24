# built-in
from argparse import ArgumentParser
from pathlib import Path

# external
from dephell_venvs import VEnvs

# app
from ..actions import get_python
from ..config import builders
from .base import BaseCommand


class VenvCreateCommand(BaseCommand):
    """Create virtual environment for current project.

    https://dephell.readthedocs.io/cmd-venv-create.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell venv create',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        if venv.exists():
            self.logger.error('venv already exists', extra=dict(path=venv.path))
            return False

        self.logger.info('creating venv for project...', extra=dict(path=venv.path))
        python = get_python(self.config)
        self.logger.info('chosen python', extra=dict(
            version=python.version,
            path=str(python.path),
        ))
        venv.create(python_path=python.path)
        self.logger.info('venv created', extra=dict(path=venv.path))
        return True

# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..controllers import DockerContainer
from .base import BaseCommand


class DockerRemoveCommand(BaseCommand):
    """Remove docker container for current project.

    https://dephell.readthedocs.io/cmd-docker-remove.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell docker remove',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        container = DockerContainer(
            path=Path(self.config['project']),
            env=self.config.env
        )
        if not container.exists():
            self.logger.error('container does not exist', extra=dict(
                container=container.container_name,
            ))
            return False

        self.logger.info('removing container...', extra=dict(
            container=container.container_name,
        ))
        container.remove()
        self.logger.info('container removed')
        return True

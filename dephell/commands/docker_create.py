# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..controllers import DockerContainer
from .base import BaseCommand


class DockerCreateCommand(BaseCommand):
    """Create docker container for current project.

    https://dephell.readthedocs.io/cmd-docker-create.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        container = DockerContainer(
            path=Path(self.config['project']),
            env=self.config.env,
            repository=self.config['docker']['repo'],
            tag=self.config['docker']['tag'],
        )
        if container.exists():
            self.logger.error('container already exists', extra=dict(
                container=container.container_name,
            ))
            return False

        self.logger.info('creating container for project...', extra=dict(
            container=container.container_name,
        ))
        container.create()
        self.logger.info('container created')
        return True

# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..controllers import DockerContainer
from .base import BaseCommand


class DockerShellCommand(BaseCommand):
    """Run shell inside of docker container.
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
        if not container.exists():
            self.logger.warning('creating container...', extra=dict(
                container=container.container_name,
            ))
            container.create()

        self.logger.info('openning shell...', extra=dict(
            container=container.container_name,
        ))
        container.activate()
        self.logger.info('closed')
        return True

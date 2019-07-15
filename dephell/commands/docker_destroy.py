# built-in
from argparse import ArgumentParser

# app
from ..actions import get_docker_container
from ..config import builders
from .base import BaseCommand


class DockerDestroyCommand(BaseCommand):
    """Remove docker container for current project.
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
        builders.build_config(parser)
        builders.build_docker(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        container = get_docker_container(config=self.config)
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

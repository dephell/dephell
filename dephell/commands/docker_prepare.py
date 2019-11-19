# built-in
from argparse import REMAINDER, ArgumentParser
from pathlib import Path

# app
from ..actions import get_docker_container
from ..config import builders
from .base import BaseCommand


class DockerPrepareCommand(BaseCommand):
    """Make docker container nice.
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser('command')
        builders.build_config(parser)
        builders.build_docker(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='command to run')
        return parser

    def __call__(self) -> bool:
        script_path = Path(__file__).parent.parent / 'templates' / 'docker_prepare.sh'
        container = get_docker_container(config=self.config)
        if not container.exists():
            self.logger.warning('creating container...', extra=dict(
                container=container.container_name,
            ))
            container.create()

        self.logger.info('running...', extra=dict(
            container=container.container_name,
        ))
        container.run(['sh', '-c', script_path.read_text()])
        self.logger.info('ready')
        return True

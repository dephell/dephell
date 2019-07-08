# built-in
import shlex
from argparse import ArgumentParser, REMAINDER
from pathlib import Path

# app
from ..config import builders
from ..controllers import DockerContainer
from .base import BaseCommand


class DockerRunCommand(BaseCommand):
    """Run command inside of docker container.
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser('command')
        builders.build_config(parser)
        builders.build_from(parser)
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

        self.logger.info('running...', extra=dict(
            container=container.container_name,
            command=command,
        ))
        container.run(command)
        self.logger.info('closed')
        return True

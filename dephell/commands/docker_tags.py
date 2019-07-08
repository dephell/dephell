# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..actions import make_json
from ..config import builders
from ..controllers import DockerContainer
from .base import BaseCommand


class DockerTagsCommand(BaseCommand):
    """Show available tags for image.
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
        print(make_json(data=container.tags, key=self.config.get('filter')))
        return True

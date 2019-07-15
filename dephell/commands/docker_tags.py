# built-in
from argparse import ArgumentParser

# app
from ..actions import get_docker_container, make_json
from ..config import builders
from .base import BaseCommand


class DockerTagsCommand(BaseCommand):
    """Show available tags for image.
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
        print(make_json(data=container.tags, key=self.config.get('filter')))
        return True

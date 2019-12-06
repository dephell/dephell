# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..actions import make_json
from ..config import builders
from ..converters import CONVERTERS
from .base import BaseCommand


class InspectProjectCommand(BaseCommand):
    """Inspect the current project.
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        if 'from' not in self.config:
            self.logger.error('`--from` is required for this command')
            return False

        loader = CONVERTERS[self.config['from']['format']]
        loader = loader.copy(project_path=Path(self.config['project']))
        root = loader.load(path=self.config['from']['path'])

        result = dict(
            name=root.raw_name,
            version=root.version,
            description=root.description,
        )
        if root.python:
            result['python'] = str(root.python)
        if root.links:
            result['links'] = root.links

        print(make_json(
            data=result,
            key=self.config.get('filter'),
            colors=not self.config['nocolors'],
            table=self.config['table'],
        ))
        return True

# built-in
from argparse import ArgumentParser
from pathlib import Path

import attr

from ..actions import make_json
from ..config import builders
# app
from ..converters import CONVERTERS
from .base import BaseCommand


class InspectProjectCommand(BaseCommand):
    """Inspect the current project.
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        if 'from' in self.config:
            # get project metainfo
            loader = CONVERTERS[self.config['from']['format']]
            loader = loader.copy(project_path=Path(self.config['project']))
            root = loader.load(path=self.config['from']['path'])
            data = attr.asdict(root)

            result = dict(
                project_name=data['raw_name'],
                version=data['version'],
                description=data['description'],
            )

            print(make_json(
                data=result,
                key=self.config.get('filter'),
                colors=not self.config['nocolors'],
                table=self.config['table'],
            ))
        return True

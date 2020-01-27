# built-in
from argparse import ArgumentParser
from pathlib import Path

# external
from dephell_versioning import get_rules

# app
from ..actions import make_json
from ..config import builders
from ..converters import CONVERTERS
from .base import BaseCommand


class InspectVersioningCommand(BaseCommand):
    """Inspect the versioning rules of the project.
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

        version = None
        if 'from' in self.config:
            loader = CONVERTERS[self.config['from']['format']]
            loader = loader.copy(project_path=Path(self.config['project']))
            root = loader.load(path=self.config['from']['path'])
            version = root.version

        scheme = self.config['versioning']
        rules = get_rules(scheme=scheme)
        data = dict(
            version=version,
            scheme=scheme,
            rules=dict(
                supported=sorted(rules),
                unsupported=sorted(get_rules() - rules),
            ),
        )

        print(make_json(
            data=data,
            key=self.config.get('filter'),
            colors=not self.config['nocolors'],
            table=self.config['table'],
        ))
        return True

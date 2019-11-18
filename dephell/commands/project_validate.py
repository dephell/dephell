# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..converters import CONVERTERS
from .base import BaseCommand


class ProjectValidateCommand(BaseCommand):
    """Check package metadata.
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        # get current deps
        if 'from' not in self.config:
            self.logger.error('`--from` is required for this command')
            return False
        loader = CONVERTERS[self.config['from']['format']]
        loader = loader.copy(project_path=Path(self.config['project']))
        root = loader.load(path=self.config['from']['path'])

        # errors
        ok = True
        if root.raw_name == 'root':
            self.logger.error('package name is unspecified')
            ok = False
        if root.raw_name != root.name:
            self.logger.error('bad name', extra=dict(
                current=root.raw_name,
                expected=root.name,
            ))
            ok = False
        if root.version == '0.0.0':
            self.logger.error('version is unspecified')
            ok = False
        if root.description and len(root.description) > 140:
            self.logger.error('short description is too long', extra=dict(
                length=len(root.description),
            ))
            ok = False
        for field in ('license', 'keywords', 'classifiers', 'description'):
            if getattr(root, field):
                continue
            self.logger.error('field is unspecified', extra=dict(field=field))
            ok = False
        if not root.package.packages:
            self.logger.error('cannot find Python files for package')
            ok = False

        # warnings
        if not root.dependencies:
            self.logger.warning('no dependencies found')

        if ok:
            self.logger.info('no errors found')
        return ok

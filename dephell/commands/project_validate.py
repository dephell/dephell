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
            self.logger.error('field is unspecified', extra=dict(field='name'))
            ok = False
        if root.raw_name != root.name:
            self.logger.error('bad name', extra=dict(
                current=root.raw_name,
                expected=root.name,
            ))
            ok = False
        if not isinstance(root.version, str):
            self.logger.error('version should be str')
            ok = False
        if root.version == '0.0.0':
            self.logger.error('field is unspecified', extra=dict(field='version'))
            ok = False
        if root.description and len(root.description) <= 10:
            self.logger.error('short description is too short', extra=dict(
                length=len(root.description),
            ))
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
        if not root.authors:
            self.logger.error('no authors specified')
            ok = False
        if not root.links:
            self.logger.error('no links specified')
            ok = False

        # classifier checks
        for classifier in root.classifiers:
            if classifier.startswith('License :: '):
                break
        else:
            self.logger.error('no license specified in classifier')
            ok = False
        for classifier in root.classifiers:
            if classifier.startswith('Development Status :: '):
                break
        else:
            self.logger.error('no development status specified in classifier')
            ok = False
        for classifier in root.classifiers:
            if classifier.startswith('Programming Language :: Python ::'):
                break
        else:
            self.logger.error('no python version specified in classifier')
            ok = False

        # warnings
        if not root.dependencies:
            self.logger.warning('no dependencies found')

        if ok:
            self.logger.info('no errors found')
        return ok

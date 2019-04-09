# built-in
from argparse import ArgumentParser

# app
from ..actions import bump_version, bump_project
from ..config import builders
from .base import BaseCommand
from ..converters import CONVERTERS
from ..models import Requirement


class ProjectBumpCommand(BaseCommand):
    """Bump project version.

    https://dephell.readthedocs.io/en/latest/cmd-project-bump.html
    """
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell project bump',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', help='bumping rule name or new version')
        return parser

    def __call__(self):
        # get project metainfo
        loader = CONVERTERS[self.config['from']['format']]
        root = loader.load(path=self.config['from']['path'])

        # make new version
        new_version = bump_version(
            version=root.version,
            rule=self.args.name,
            scheme=self.config['versioning'],
        )
        self.logger.info('generated new version', extra=dict(
            old=root.version,
            new=new_version,
        ))

        # update version in project files
        for path in bump_project(project=root.package, old=root.version, new=new_version):
            self.logger.info('file bumped', extra=dict(path=str(path)))

        # update version in project metadata
        root.version = new_version
        loader.dump(
            project=root,
            path=self.config['from']['path'],
            reqs=[Requirement(dep=dep, lock=loader.lock) for dep in root.dependencies],
        )
        return True

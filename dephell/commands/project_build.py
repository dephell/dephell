# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..actions import attach_deps
from ..config import builders
from ..controllers import analyze_conflict
from ..converters import CONVERTERS
from ..models import Requirement
from .base import BaseCommand


DUMPERS = (
    ('setuppy', 'setup.py'),
    ('egginfo', '.'),
    ('sdist', 'dist/'),
    ('wheel', 'dist/'),
)


class ProjectBuildCommand(BaseCommand):
    """Create dist archives for project.

    https://dephell.readthedocs.io/en/latest/cmd-project-build.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell project build',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_resolver(parser)
        builders.build_api(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        loader = CONVERTERS[self.config['from']['format']]
        resolver = loader.load_resolver(path=self.config['from']['path'])
        if loader.lock:
            self.logger.warning('do not build project from lockfile!')

        # attach
        merged = attach_deps(resolver=resolver, config=self.config, merge=True)
        if not merged:
            conflict = analyze_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # dump
        project_path = Path(self.config['project'])
        reqs = Requirement.from_graph(resolver.graph, lock=False)
        for to_format, to_path in DUMPERS:
            if to_format == self.config['from']['format']:
                continue
            self.logger.info('dumping...', extra=dict(format=to_format))
            dumper = CONVERTERS[to_format]
            dumper.dump(
                path=project_path.joinpath(to_path),
                reqs=reqs,
                project=resolver.graph.metainfo,
            )

        self.logger.info('builded')
        return True

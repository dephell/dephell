# built-in
from argparse import ArgumentParser

# app
from ..actions import attach_deps
from ..config import builders
from ..controllers import analyze_conflict
from ..converters import CONVERTERS
from ..models import Requirement
from .base import BaseCommand


class DepsConvertCommand(BaseCommand):
    """Convert dependencies between formats.

    https://dephell.readthedocs.io/en/latest/cmd-deps-convert.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell deps convert',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_to(parser)
        builders.build_resolver(parser)
        builders.build_api(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        loader = CONVERTERS[self.config['from']['format']]
        dumper = CONVERTERS[self.config['to']['format']]

        # load
        self.logger.debug('load dependencies...', extra=dict(
            format=self.config['from']['format'],
            path=self.config['from']['path'],
        ))
        resolver = loader.load_resolver(path=self.config['from']['path'])
        should_be_resolved = not loader.lock and dumper.lock

        # attach
        merged = attach_deps(resolver=resolver, config=self.config, merge=not should_be_resolved)
        if not merged:
            conflict = analyze_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # resolve (and merge)
        if should_be_resolved:
            self.logger.debug('resolving...')
            resolved = resolver.resolve(silent=self.config['silent'])
            if not resolved:
                conflict = analyze_conflict(resolver=resolver)
                self.logger.warning('conflict was found')
                print(conflict)
                return False
            self.logger.debug('resolved')

        # dump
        self.logger.debug('dump dependencies...', extra=dict(
            format=self.config['to']['format'],
            path=self.config['to']['path'],
        ))
        dumper.dump(
            path=self.config['to']['path'],
            reqs=Requirement.from_graph(resolver.graph, lock=dumper.lock),
            project=resolver.graph.metainfo,
        )
        self.logger.info('converted')
        return True

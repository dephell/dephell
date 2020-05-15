# built-in
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict

# app
from ..actions import attach_deps
from ..config import builders
from ..controllers import analyze_conflict
from ..converters import CONVERTERS
from ..models import Requirement
from .base import BaseCommand


class DepsConvertCommand(BaseCommand):
    """Convert dependencies between formats.
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_to(parser)
        builders.build_resolver(parser)
        builders.build_api(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        if 'from' not in self.config:
            self.logger.error('`--from` is required for this command')
            return False
        if 'to' not in self.config:
            self.logger.error('`--to` is required for this command')
            return False
        loader = CONVERTERS[self.config['from']['format']]
        loader = loader.copy(project_path=Path(self.config['project']))
        dumper = CONVERTERS[self.config['to']['format']]
        dumper = dumper.copy(project_path=Path(self.config['project']))

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

        # filter out deps by `--envs`
        if self.config.get('envs'):
            if not should_be_resolved:
                resolver.graph.fast_apply()
            resolver.apply_envs(envs=set(self.config['envs']), deep=should_be_resolved)
            # If it's not a lockfile, we should drop all dependencies except direct ones.
            # While `fast_apply` doesn't produce such dependencies, we want to be sure
            # that we can't ever have them in the output. Trust no one.
            if not should_be_resolved:
                resolver.graph._layers = resolver.graph._layers[:2]

        # dump
        self.logger.debug('dump dependencies...', extra=dict(
            format=self.config['to']['format'],
            path=self.config['to']['path'],
        ))

        dumper_kwargs = dict(
            reqs=Requirement.from_graph(resolver.graph, lock=dumper.lock),
            project=resolver.graph.metainfo,
        )  # type: Dict[str, Any]
        if self.config['to']['path'] == 'stdout':
            print(dumper.dumps(**dumper_kwargs))
        else:
            dumper.dump(path=self.config['to']['path'], **dumper_kwargs)
        self.logger.info('converted')
        return True

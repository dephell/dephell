# built-in
import json
from argparse import ArgumentParser
from collections import defaultdict

# app
from ..config import builders
from ..controllers import analize_conflict
from ..converters import CONVERTERS
from .base import BaseCommand


class DepsLicensesCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell deps licenses',
            description='Show licenses for all project dependencies',
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_resolver(parser)
        builders.build_api(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self):
        loader = CONVERTERS[self.config['from']['format']]
        resolver = loader.load_resolver(path=self.config['from']['path'])

        # attach
        if self.config.get('and'):
            for source in self.config['and']:
                loader = CONVERTERS[source['format']]
                root = loader.load(path=source['path'])
                resolver.graph.add(root)

        # resolve (and merge)
        resolved = resolver.resolve()
        if not resolved:
            conflict = analize_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False
        self.logger.info('resolved')

        # get licenses
        licenses = defaultdict(set)
        for dep in resolver.graph:
            if dep.license:
                license = dep.license if isinstance(dep.license, str) else dep.license.name
                licenses[license].add(dep.name)
            else:
                licenses['Unknown License'].add(dep.name)
        licenses = {name: sorted(deps) for name, deps in licenses.items()}
        print(json.dumps(licenses, sort_keys=True, indent=2))
        return True

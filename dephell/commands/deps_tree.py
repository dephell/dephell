# built-in
from argparse import ArgumentParser

# app
from ..config import builders
from ..controllers import analize_conflict
from ..converters import CONVERTERS
from .base import BaseCommand


class DepsTreeCommand(BaseCommand):
    """Show dependencies tree

    https://dephell.readthedocs.io/en/latest/cmd-deps-tree.html
    """
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell deps tree',
            description=cls.__doc__,
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

        # resolve
        self.logger.debug('resolving...')
        resolved = resolver.resolve()
        if not resolved:
            conflict = analize_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False
        self.logger.debug('resolved')

        for dep in sorted(resolver.graph.get_layer(1)):
            self._print_dep(dep)
        return True

    @classmethod
    def _print_dep(cls, dep, *, level: int = 0):
        print('{level}- {name} [required: {constraint}, locked: {best}, latest: {latest}]'.format(
            level='  ' * level,
            name=dep.name,
            constraint=str(dep.constraint) or '*',
            best=str(dep.group.best_release.version),
            latest=str(dep.groups.releases[0].version),
        ))
        for subdep in sorted(dep.dependencies):
            cls._print_dep(subdep, level=level + 1)

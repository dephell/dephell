# built-in
from argparse import REMAINDER, ArgumentParser
from typing import List

# app
from ..actions import make_json, get_resolver
from ..config import builders
from .base import BaseCommand


class DepsTreeCommand(BaseCommand):
    """Show dependencies tree.

    https://dephell.readthedocs.io/cmd-deps-tree.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
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
        parser.add_argument('--type', choices=('pretty', 'json', 'graph'), default='pretty',
                            help='format for tree output.')
        parser.add_argument('name', nargs=REMAINDER, help='package to get dependencies from')
        return parser

    def __call__(self) -> bool:
        if self.args.name:
            resolver = get_resolver(reqs=self.args.name)
            resolver = self._resolve(resolver=resolver)
        else:
            resolver = self._get_locked()
        if resolver is None:
            return False

        if self.args.type == 'pretty':
            for dep in sorted(resolver.graph.get_layer(1)):
                print('\n'.join(self._make_tree(dep)))
            return True

        if self.args.type == 'json':
            result = []
            for dep in sorted(resolver.graph):
                result.append(dict(
                    name=dep.name,
                    constraint=str(dep.constraint) or '*',
                    best=str(dep.group.best_release.version),
                    latest=str(dep.groups.releases[0].version),
                    dependencies=[subdep.name for subdep in dep.dependencies],
                ))
            print(make_json(result, key=self.config.get('filter')))
            return True

        if self.args.type == 'graph':
            resolver.graph.draw()
            self.logger.info('graph saved into .dephell_report/')
            return True

    @classmethod
    def _make_tree(cls, dep, *, level: int = 0) -> List[str]:
        lines = ['{level}- {name} [required: {constraint}, locked: {best}, latest: {latest}]'.format(
            level='  ' * level,
            name=dep.name,
            constraint=str(dep.constraint) or '*',
            best=str(dep.group.best_release.version),
            latest=str(dep.groups.releases[0].version),
        )]
        deps = {dep.name: dep for dep in dep.dependencies}.values()  # drop duplicates
        for subdep in sorted(deps):
            lines.extend(cls._make_tree(subdep, level=level + 1))
        return lines

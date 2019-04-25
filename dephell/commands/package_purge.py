# built-in
from argparse import ArgumentParser

from packaging.utils import canonicalize_name

# app
from ..actions import get_python_env
from ..config import builders
from ..controllers import analyze_conflict, Resolver, Mutator, Graph
from ..converters import InstalledConverter
from ..models import Requirement
from ..package_manager import PackageManager
from .base import BaseCommand


class PackagePurgeCommand(BaseCommand):
    """Remove given packages and their dependencies.

    https://dephell.readthedocs.io/en/latest/cmd-package-purge.html
    """

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell package purge',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs='+', help='names of packages to remove')
        return parser

    def __call__(self) -> bool:
        python = get_python_env(config=self.config)
        manager = PackageManager(executable=python.path)
        converter = InstalledConverter()

        # get installed packages
        root = converter.load(paths=python.lib_paths)
        names = set(self.args.name) & {canonicalize_name(dep.name) for dep in root.dependencies}
        if not names:
            self.logger.error('packages is not installed', extra=dict(python=python.path))
            return False

        # resolve graph
        self.logger.info('build dependencies graph...')
        resolver = Resolver(
            graph=Graph(root),
            mutator=Mutator(),
        )
        resolved = resolver.resolve(silent=self.config['silent'])
        if not resolved:
            conflict = analyze_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # get packages to remove
        reqs = []
        for name in names:
            parent = resolver.graph.get(name=name)
            reqs.append(Requirement(dep=parent, lock=True))

            for dep in resolver.graph.get_children(dep=parent).values():
                if not dep:
                    raise LookupError('cannot find dep in graph')
                if dep.constraint.sources - {root.name} - names:
                    continue
                reqs.append(Requirement(dep=dep, lock=True))

        # remove installed packages
        self.logger.info('removing packages...', extra=dict(
            python=python.path,
            packages=[req.name for req in reqs],
        ))
        code = manager.remove(reqs=reqs)
        if code != 0:
            return False
        self.logger.info('removed')
        return True

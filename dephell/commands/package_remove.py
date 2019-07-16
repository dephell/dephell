# built-in
from argparse import ArgumentParser

# app
from ..actions import get_python_env
from ..config import builders
from ..controllers import Graph
from ..converters import InstalledConverter
from ..models import Requirement
from ..package_manager import PackageManager
from .base import BaseCommand


class PackageRemoveCommand(BaseCommand):
    """Remove installed packages.
    """

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
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
        root = converter.load(paths=python.lib_paths, names=self.args.name)
        if not root.dependencies:
            self.logger.error('packages is not installed', extra=dict(python=python.path))
            return False

        # remove installed packages
        self.logger.info('removing packages...', extra=dict(
            packages=len(root.dependencies),
            python=python.path,
        ))
        reqs = Requirement.from_graph(graph=Graph(root), lock=True)
        code = manager.remove(reqs=reqs)
        if code != 0:
            return False
        self.logger.info('removed')
        return True

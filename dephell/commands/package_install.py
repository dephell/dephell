# built-in
from argparse import REMAINDER, ArgumentParser

# app
from ..actions import get_python_env, get_resolver
from ..config import builders
from ..controllers import analyze_conflict
from ..models import Requirement
from ..package_manager import PackageManager
from .base import BaseCommand


class PackageInstallCommand(BaseCommand):
    """Download and install package into project environment.

    https://dephell.readthedocs.io/en/latest/cmd-package-install.html
    """

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell package install',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_resolver(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='package to install')
        return parser

    def __call__(self) -> bool:
        # resolve
        resolver = get_resolver(reqs=self.args.name)
        self.logger.info('build dependencies graph...')
        resolved = resolver.resolve(silent=self.config['silent'])
        if not resolved:
            conflict = analyze_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # get executable
        python = get_python_env(config=self.config)

        # install
        reqs = Requirement.from_graph(graph=resolver.graph, lock=True)
        self.logger.info('installation...', extra=dict(
            executable=str(python.path),
            packages=len(reqs),
        ))
        code = PackageManager(executable=python.path).install(reqs=reqs)
        if code != 0:
            return False
        self.logger.info('installed')
        return True

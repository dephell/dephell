# built-in
from argparse import REMAINDER, ArgumentParser

# app
from ..actions import get_python_env, get_resolver, install_deps
from ..config import builders
from .base import BaseCommand


class PackageInstallCommand(BaseCommand):
    """Download and install package into project environment.
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_resolver(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='package to install')
        return parser

    def __call__(self) -> bool:
        # get executable
        python = get_python_env(config=self.config)

        # install
        resolver = get_resolver(reqs=self.args.name)
        return install_deps(
            resolver=resolver,
            python_path=python.path,
            logger=self.logger,
            silent=self.config['silent'],
        )

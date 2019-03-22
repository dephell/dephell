# built-in
import sys
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..controllers import analize_conflict
from ..converters import CONVERTERS
from ..models import Requirement
from ..package_manager import PackageManager
from ..venvs import VEnvs
from .base import BaseCommand


class InstallCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell install',
            description='Install project dependencies',
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_resolver(parser)
        builders.build_api(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        loader_config = self.config.get('to', self.config['from'])
        self.logger.info('get dependencies', extra=dict(
            format=loader_config['format'],
            path=loader_config['path'],
        ))
        loader = CONVERTERS[loader_config['format']]
        resolver = loader.load_resolver(path=loader_config['path'])

        # attach
        if self.config.get('and'):
            for source in self.config['and']:
                loader = CONVERTERS[source['format']]
                root = loader.load(path=source['path'])
                resolver.graph.add(root)

        # resolve (and merge)
        self.logger.info('build dependencies graph...')
        resolved = resolver.resolve()
        if not resolved:
            conflict = analize_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # get executable
        executable = Path(sys.executable)
        venvs = VEnvs(path=self.config['venv'], env=self.config.env)
        venv = venvs.current
        if venv is not None:
            executable = venv.python_path
        else:
            venv = venvs.get(Path(self.config['project']))
            if venv.exists():
                executable = venv.python_path

        # install
        reqs = Requirement.from_graph(graph=resolver.graph, lock=True)
        self.logger.info('installation...', extra=dict(
            executable=executable,
            packages=len(reqs),
        ))
        PackageManager(executable=executable).install(reqs=reqs)
        self.logger.info('installed')

        return True

# built-in
import sys
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..controllers import analize_conflict
from ..converters import CONVERTERS
from ..models import Requirement
from .base import BaseCommand
from ..venvs import VEnvs
from ..package_manager import PackageManager


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
        PackageManager(executable=sys.executable).run('install', 'django')
        return False

        loader_config = self.config.get('to', self.config['from'])
        loader = CONVERTERS[loader_config['format']]
        resolver = loader.load_resolver(path=self.config['from']['path'])

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
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.current
        if venv is not None:
            executable = venv.python_path
        else:
            venv = venvs.get(path=Path(self.config['project']))
            if venv.exists():
                executable = venv.python_path

        # install
        self.logger.info('installation...')
        reqs = Requirement.from_graph(graph=resolver.graph)
        PackageManager(executable=executable).install(reqs=reqs)

        return True

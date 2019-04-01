# built-in
import sys
from argparse import ArgumentParser, REMAINDER
from pathlib import Path

# app
from ..config import builders
from ..controllers import analize_conflict
from ..converters import PIPConverter
from ..models import Requirement
from ..package_manager import PackageManager
from ..venvs import VEnvs
from .base import BaseCommand


class PackageInstallCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell package install',
            description='Download and install package into project environment',
        )
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='package to install')
        return parser

    def __call__(self) -> bool:
        # resolve
        resolver = PIPConverter(lock=False).loads_resolver(' '.join(self.args.name))
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
            venv = venvs.get(Path(self.config['project']), env=self.config.env)
            if venv.exists():
                executable = venv.python_path

        # install
        reqs = Requirement.from_graph(graph=resolver.graph, lock=True)
        self.logger.info('installation...', extra=dict(
            executable=executable,
            packages=len(reqs),
        ))
        code = PackageManager(executable=executable).install(reqs=reqs)
        if code != 0:
            return False
        self.logger.info('installed')
        return True

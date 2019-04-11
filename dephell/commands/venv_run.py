# built-in
import shlex
import subprocess
from argparse import REMAINDER, ArgumentParser
from pathlib import Path

# project
from dephell_venvs import VEnvs

# app
from ..actions import get_python, get_resolver
from ..config import builders
from ..controllers import analize_conflict
from ..models import Requirement
from ..package_manager import PackageManager
from .base import BaseCommand


class VenvRunCommand(BaseCommand):
    """Run command in the project virtual environment

    https://dephell.readthedocs.io/en/latest/cmd-venv-run.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell venv run',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_api(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='command to run')
        return parser

    def __call__(self) -> bool:
        command = self.args.name
        if not command:
            command = self.config.get('command')
            if not command:
                self.logger.error('command required')
                return False
        if isinstance(command, str):
            command = shlex.split(command)

        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(Path(self.config['project']), env=self.config.env)
        if not venv.exists():
            self.logger.warning('venv does not exist, creating...', extra=dict(
                project=self.config['project'],
                env=self.config.env,
                path=str(venv.path),
            ))
            python = get_python(self.config)
            self.logger.debug('choosen python', extra=dict(version=python.version))
            venv.create(python_path=python.path)
            self.logger.info('venv created', extra=dict(path=venv.path))

        executable = venv.bin_path / command[0]
        if not executable.exists():
            self.logger.warning('executable does not found in venv, trying to install...', extra=dict(
                executable=command[0],
            ))
            result = self._install(name=command[0], python_path=venv.python_path)
            if not result:
                return False

        result = subprocess.run([str(executable)] + command[1:])
        return not result.returncode

    def _install(self, name: str, python_path: Path) -> bool:
        # resolve
        resolver = get_resolver(reqs=[name])
        self.logger.info('build dependencies graph...')
        resolved = resolver.resolve(silent=self.config['silent'])
        if not resolved:
            conflict = analize_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # install
        reqs = Requirement.from_graph(graph=resolver.graph, lock=True)
        self.logger.info('installation...', extra=dict(
            executable=python_path,
            packages=len(reqs),
        ))
        code = PackageManager(executable=python_path).install(reqs=reqs)
        if code != 0:
            return False
        self.logger.info('installed')
        return True

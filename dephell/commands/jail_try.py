# built-in
import shlex
import subprocess
from argparse import REMAINDER, ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Set

# external
from dephell_venvs import VEnv

# app
from ..actions import get_python, get_resolver
from ..config import builders
from ..context_tools import override_env_vars
from ..controllers import analyze_conflict
from ..models import Requirement
from ..package_manager import PackageManager
from .base import BaseCommand


class JailTryCommand(BaseCommand):
    """Try packages into temporary isolated environment.

    https://dephell.readthedocs.io/en/latest/cmd-jail-try.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell jail try',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('--command', help='command to execute.')
        parser.add_argument('name', nargs=REMAINDER, help='packages to install')
        return parser

    def __call__(self) -> bool:
        resolver = get_resolver(reqs=self.args.name)
        name = next(iter(resolver.graph.get_layer(0))).dependencies[0].name

        command = self.config.get('command')
        if not command:
            command = 'python'
        if isinstance(command, str):
            command = shlex.split(command)

        with TemporaryDirectory() as base_path:
            base_path = Path(base_path)

            # make venv
            venv = VEnv(path=base_path)
            if venv.exists():
                self.logger.error('already installed', extra=dict(package=name))
                return False
            python = get_python(self.config)
            self.logger.info('creating venv...', extra=dict(
                venv=str(venv.path),
                python=str(python.path),
            ))
            venv.create(python_path=python.path)

            # install
            ok = self._install(resolver=resolver, python_path=venv.python_path)
            if not ok:
                return False

            # install executable
            executable = venv.bin_path / command[0]
            if not executable.exists():
                self.logger.warning('executable is not found in venv, trying to install...', extra=dict(
                    executable=command[0],
                ))
                ok = self._install(
                    resolver=get_resolver(reqs=command[:1]),
                    python_path=venv.python_path,
                )
                if not ok:
                    return False
            if not executable.exists():
                self.logger.error('package installed, but executable is not found')
                return False

            # make startup script to import installed packages
            startup_path = base_path / '_startup.py'
            packages = self._get_startup_packages(lib_path=venv.lib_path, packages=self.args.name)
            if not packages:
                self.logger.error('cannot find any packages')
                return False
            startup_path.write_text('import ' + ', '.join(sorted(packages)))

            # run
            self.logger.info('running...')
            with override_env_vars({'PYTHONSTARTUP': str(startup_path)}):
                result = subprocess.run([str(executable)] + command[1:])
            if result.returncode != 0:
                self.logger.error('command failed', extra=dict(code=result.returncode))
                return False

            return True

    def _install(self, resolver, python_path: Path) -> bool:
        self.logger.info('build dependencies graph...')
        resolved = resolver.resolve(silent=self.config['silent'])
        if not resolved:
            conflict = analyze_conflict(resolver=resolver)
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

    @staticmethod
    def _get_startup_packages(lib_path: Path, packages) -> Set[str]:
        names = set()
        for path in lib_path.iterdir():
            name = path.name
            if name == '__pycache__':
                continue
            if name.endswith('.py'):
                names.add(name.split('.')[0])
            elif path.is_dir() and '.' not in name:
                names.add(name)

        if packages:
            packages = {package.lower().replace('-', '_') for package in packages}
            if len(names & packages) == len(packages):
                return packages

        return names

# built-in
import shutil
from argparse import REMAINDER, ArgumentParser
from pathlib import Path

# external
from dephell_venvs import VEnvs

# app
from ..actions import get_entrypoints, get_python, get_resolver
from ..config import builders
from ..constants import IS_WINDOWS
from ..controllers import analyze_conflict
from ..models import Requirement
from ..package_manager import PackageManager
from .base import BaseCommand


class JailInstallCommand(BaseCommand):
    """Download and install package into isolated environment.

    https://dephell.readthedocs.io/cmd-jail-install.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell jail install',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_resolver(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='packages to install')
        return parser

    def __call__(self) -> bool:
        resolver = get_resolver(reqs=self.args.name)
        name = next(iter(resolver.graph.get_layer(0))).dependencies[0].name

        # resolve (and merge)
        self.logger.info('build dependencies graph...')
        resolved = resolver.resolve(silent=self.config['silent'])
        if not resolved:
            conflict = analyze_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # make venv
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get_by_name(name)
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
        reqs = Requirement.from_graph(graph=resolver.graph, lock=True)
        self.logger.info('installation...', extra=dict(
            executable=venv.python_path,
            packages=len(reqs),
        ))
        code = PackageManager(executable=venv.python_path).install(reqs=reqs)
        if code != 0:
            return False

        # get entrypoints
        entrypoints = get_entrypoints(venv=venv, name=name)
        if entrypoints is None:
            return False

        # copy console scripts
        self.logger.info('copy executables...', extra=dict(package=name, path=self.config['bin']))
        for entrypoint in entrypoints:
            if entrypoint.group != 'console_scripts':
                continue
            if not (venv.bin_path / entrypoint.name).exists():
                self.logger.error('cannot find script in venv', extra=dict(script=entrypoint.name))
            else:
                self._publish_script(
                    src=venv.bin_path / entrypoint.name,
                    dst=Path(self.config['bin']) / entrypoint.name,
                )
                self.logger.info('copied', extra=dict(script=entrypoint.name))

        return True

    @staticmethod
    def _publish_script(src: Path, dst: Path):
        if dst.exists() or dst.is_symlink():
            dst.unlink()
        if IS_WINDOWS:
            shutil.copy(str(src), str(dst))
        else:
            # Python 3.5 cannot resove non-existing paths.
            dst = dst.parent.resolve() / dst.name
            dst.symlink_to(src)

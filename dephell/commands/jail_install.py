# built-in
import shutil
from argparse import REMAINDER, ArgumentParser
from pathlib import Path

# external
from dephell_venvs import VEnvs

# app
from ..actions import get_entrypoints, get_python, get_resolver, install_deps
from ..config import builders
from ..constants import IS_WINDOWS
from .base import BaseCommand


class JailInstallCommand(BaseCommand):
    """Download and install package into isolated environment.
    """
    find_config = False

    @staticmethod
    def build_parser(parser) -> ArgumentParser:
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
        ok = install_deps(
            resolver=resolver,
            python_path=venv.python_path,
            logger=self.logger,
            silent=self.config['silent'],
        )
        if not ok:
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

            entrypoint_filename = entrypoint.name
            if IS_WINDOWS:
                entrypoint_filename += '.exe'

            if not (venv.bin_path / entrypoint_filename).exists():
                self.logger.error('cannot find script in venv', extra=dict(script=entrypoint.name))
                continue
            self._publish_script(
                src=venv.bin_path / entrypoint_filename,
                dst=Path(self.config['bin']) / entrypoint_filename,
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
            dst = dst.parent.resolve() / dst.name
            dst.symlink_to(src)

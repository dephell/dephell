# built-in
import shlex
from argparse import REMAINDER, ArgumentParser
from pathlib import Path

# external
from dephell_venvs import VEnvs

# app
from ..actions import get_python, install_dep
from ..config import builders
from .base import BaseCommand


class VenvEntrypointCommand(BaseCommand):
    """Create binary to run a command in the venv.
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('--command', help='command to run')
        parser.add_argument('name', nargs=REMAINDER, help='executable name to create')
        return parser

    def __call__(self) -> bool:
        project_path = Path(self.config['project'])

        command = self.config.get('command')
        if not command:
            self.logger.error('command required')
            return False
        if isinstance(command, str):
            command = shlex.split(command)

        # get and make venv
        venvs = VEnvs(path=self.config['venv'])
        venv = venvs.get(project_path, env=self.config.env)
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

        # install executable
        executable = venv.bin_path / command[0]
        if not executable.exists():
            self.logger.warning('executable is not found in venv, trying to install...', extra=dict(
                executable=command[0],
            ))
            result = install_dep(
                name=command[0],
                python_path=venv.python_path,
                logger=self.logger,
                silent=self.config['silent'],
            )
            if not result:
                return False
        if not executable.exists():
            self.logger.error('package installed, but executable is not found')
            return False

        # write script
        entrypoint_filename = '-'.join(self.args.name)
        if not entrypoint_filename:
            entrypoint_filename = '{}-{}'.format(project_path.name, executable.stem)
        script = self._make_script(command=command, executable=executable)
        self.logger.debug(script)
        path = Path(self.config['bin']) / entrypoint_filename
        exists = path.exists()
        path.touch(mode=0o770)
        path.write_text(script)

        if exists:
            self.logger.info('script updated', extra=dict(path=path))
        else:
            self.logger.info('script created', extra=dict(path=path))
        return True

    def _make_script(self, command: list, executable: Path) -> str:
        script = ['#!/usr/bin/env bash']

        if 'vars' in self.config:
            for name, value in self.config['vars'].items():
                script.append('export {n}="{v}"'.format(n=name, v=value))

        dotenv = Path(self.config['dotenv'])
        if dotenv.is_dir():
            dotenv = dotenv / '.env'
        if dotenv.exists():
            script.append('. {}'.format(str(dotenv)))

        project_path = Path(self.config['project']).absolute()
        script.append('cd {}'.format(str(project_path)))

        script.append('{exe} {args} $@'.format(
            exe=str(executable),
            args=' '.join(command[1:]),
        ))
        return '\n'.join(script) + '\n'

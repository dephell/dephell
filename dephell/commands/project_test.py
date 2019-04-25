# built-in
import shlex
import shutil
import subprocess
from argparse import REMAINDER, ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory

# external
from dephell_pythons import Pythons
from dephell_venvs import VEnv

# app
from ..actions import attach_deps
from ..config import builders
from ..controllers import analyze_conflict
from ..converters import CONVERTERS, WheelConverter
from ..models import Requirement
from .base import BaseCommand


class ProjectTestCommand(BaseCommand):
    """Test project build in temporary venvs.

    https://dephell.readthedocs.io/en/latest/cmd-project-test.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell project test',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='command to run')
        return parser

    def __call__(self) -> bool:
        # load project
        loader = CONVERTERS[self.config['from']['format']]
        resolver = loader.load_resolver(path=self.config['from']['path'])
        if loader.lock:
            self.logger.warning('do not build project from lockfile!')

        # attach
        merged = attach_deps(resolver=resolver, config=self.config, merge=True)
        if not merged:
            conflict = analyze_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # dump
        project_path = Path(self.config['project'])
        reqs = Requirement.from_graph(resolver.graph, lock=False)
        self.logger.info('creating wheel...')
        dumper = WheelConverter()
        project = resolver.graph.metainfo
        dumper.dump(path=project_path / 'dist', reqs=reqs, project=project)
        wheel_path = dumper._get_path(path=project_path / 'dist', project=project)

        # get command
        command = self.args.name
        if not command:
            command = self.config.get('command')
            if not command:
                self.logger.error('command required')
                return False
        if isinstance(command, str):
            command = shlex.split(command)

        # choose pythons
        self.logger.info('get interpreters')
        pythons = Pythons()
        if 'python' in self.config:
            # get from config
            choosen_pythons = (pythons.get_best(self.config['python']), )
        else:
            # get from project
            choosen_pythons = dict()
            pyrhon_constraint = resolver.graph.metainfo.python
            for python in pythons:
                version = str(python.get_short_version())
                if version in choosen_pythons:
                    continue
                if python.version not in pyrhon_constraint:
                    continue
                choosen_pythons[version] = python
            choosen_pythons = tuple(choosen_pythons.values())

        for python in choosen_pythons:
            with TemporaryDirectory() as path:
                root_path = Path(path)

                # make venv
                self.logger.info('create venv', extra=dict(python=str(python.version)))
                venv = VEnv(path=root_path / 'venv')
                venv.create(python_path=python.path)

                # copy tests
                for path in self.config['tests']:
                    self.logger.info('copy files', extra=dict(path=path))
                    path = Path(path)
                    if not path.exists():
                        raise FileNotFoundError(str(path))

                    # copy file
                    if path.is_file():
                        shutil.copyfile(str(path), str(root_path / path.name))
                        continue

                    # copy dir
                    for subpath in path.glob('**/*'):
                        if not subpath.is_file():
                            continue
                        if '__pycache__' in subpath.parts:
                            continue
                        new_path = subpath.resolve().relative_to(self.config['project'])
                        new_path = root_path.joinpath(new_path)
                        self.logger.debug('copy', extra=dict(old=str(subpath), new=str(new_path)))
                        new_path.parent.mkdir(exist_ok=True, parents=True)
                        shutil.copyfile(str(subpath), str(new_path))

                # install project
                self.logger.info('install project', extra=dict(path=str(wheel_path)))
                result = subprocess.run(
                    [str(venv.bin_path / 'pip'), 'install', str(wheel_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if result.returncode != 0:
                    self.logger.error('failed to install project')
                    self.logger.error(result.stderr.decode())
                    return False

                # install executable
                executable = venv.bin_path / command[0]
                if not executable.exists():
                    self.logger.info('executable not found, installing', extra=dict(
                        executable=command[0],
                    ))
                    result = subprocess.run(
                        [str(venv.bin_path / 'pip'), 'install', command[0]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    if result.returncode != 0:
                        self.logger.error('failed to install tests executable')
                        self.logger.error(result.stderr.decode())
                        return False

                # run tests
                self.logger.info('run tests', extra=dict(command=command))
                result = subprocess.run(
                    [str(executable)] + command[1:],
                    cwd=str(root_path),
                )
                if result.returncode != 0:
                    self.logger.error('command failed, stopping')
                    return False

        return True

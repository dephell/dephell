# built-in
import sys
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..controllers import analize_conflict
from ..converters import CONVERTERS, InstalledConverter
from ..models import Requirement
from ..package_manager import PackageManager
from ..venvs import VEnvs
from .base import BaseCommand


class DepsInstallCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell deps install',
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

        # resolve
        self.logger.info('build dependencies graph...')
        resolved = resolver.resolve()
        if not resolved:
            conflict = analize_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # filter deps by envs
        resolver.apply_envs(set(self.config['envs']))

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

        # get installed packages
        installed_root = InstalledConverter().load(path=venv.lib_path)
        installed = {dep.name: str(dep.constraint).strip('=') for dep in installed_root.dependencies}

        # plan what we will install and what we will remove
        install = []
        remove = []
        for req in Requirement.from_graph(graph=resolver.graph, lock=True):
            # not installed, install
            if req.name not in installed:
                install.append(req)
                continue
            # installed the same version, skip
            version = req.version.strip('=')
            if version == installed[req.name]:
                continue
            # installed old version, remove it and install new
            self.logger.debug('dependency will be updated', extra=dict(
                dependency=req.name,
                old=installed[req.name],
                new=version,
            ))
            remove.append(req)
            install.append(req)

        # remove
        manager = PackageManager(executable=executable)
        if remove:
            self.logger.info('removing old packages...', extra=dict(
                executable=executable,
                packages=len(remove),
            ))
            code = manager.remove(reqs=remove)
            if code != 0:
                return False

        # install
        if install:
            self.logger.info('installation...', extra=dict(
                executable=executable,
                packages=len(install),
            ))
            code = manager.install(reqs=install)
            if code != 0:
                return False

        self.logger.info('installed')
        return True

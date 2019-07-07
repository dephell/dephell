# built-in
from argparse import ArgumentParser
from types import SimpleNamespace
from typing import Tuple

# app
from ..actions import get_python_env
from ..config import builders
from ..converters import InstalledConverter
from ..models import Requirement
from ..package_manager import PackageManager
from .base import BaseCommand


class DepsInstallCommand(BaseCommand):
    """Install project dependencies.

    https://dephell.readthedocs.io/cmd-deps-install.html
    """
    sync = False

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell deps install',
            description=cls.__doc__,
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
        resolver = self._get_locked(default_envs={'main'})
        if resolver is None:
            return False

        python = get_python_env(config=self.config)
        self.logger.debug('choosen python', extra=dict(path=str(python.path)))
        resolver.apply_markers(python=python)
        install, remove = self._get_install_remove(graph=resolver.graph, python=python)

        # remove
        manager = PackageManager(executable=python.path)
        if remove:
            self.logger.info('removing old packages...', extra=dict(
                executable=python.path,
                packages=len(remove),
            ))
            code = manager.remove(reqs=remove)
            if code != 0:
                return False

        # install
        if install:
            self.logger.info('installation...', extra=dict(
                executable=python.path,
                packages=len(install),
            ))
            code = manager.install(reqs=install)
            if code != 0:
                return False

        if not install and not remove:
            self.logger.info('everything is up-to-date')
        else:
            self.logger.info('synced' if self.sync else 'installed')
        return True

    def _get_install_remove(self, graph, python) -> Tuple[list, list]:
        # get installed packages
        installed_root = InstalledConverter().load(paths=python.lib_paths)
        installed = {dep.name: str(dep.constraint).strip('=') for dep in installed_root.dependencies}

        # plan what we will install and what we will remove
        install = []
        remove = []
        reqs = Requirement.from_graph(graph=graph, lock=True)
        for req in reqs:
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

        # remove packages not in graph
        if self.sync:
            names = set(installed) - {req.name for req in reqs}
            remove.extend(SimpleNamespace(name=name) for name in names)

        return install, remove

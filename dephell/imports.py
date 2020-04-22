# built-in
import sys
from importlib import import_module
from logging import getLogger
from pathlib import Path


logger = getLogger(__name__)


class LazyModule:
    def __init__(self, name: str, package: str = None):
        self._name = name
        self._package = package

    @property
    def _module(self):
        try:
            return import_module(name=self._name)
        except ImportError:
            self._install()
        return import_module(name=self._name)

    def _install(self):
        from .package_manager import PackageManager

        name = self._package or self._name.split('.', maxsplit=1)[0]
        msg = 'cannot find module, trying to install'
        logger.warning(msg, extra=dict(package=name))

        manager = PackageManager(executable=Path(sys.executable))
        args = ['install']
        if manager.is_global:
            args.append('--user')
        args.append(name)
        code = manager.run(*args)
        if code != 0:
            raise RuntimeError('cannot install package {}'.format(name))

    def __getattr__(self, name: str):
        if name[0] == '_':
            raise AttributeError(name)
        return getattr(self._module, name)

    def __dir__(self):
        return dir(self._module)


def lazy_import(name: str, package: str = None) -> LazyModule:
    return LazyModule(name=name, package=package)

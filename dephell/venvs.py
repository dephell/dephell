
# built-in
import os
import shutil
from base64 import b64encode
from hashlib import md5
from itertools import chain
from pathlib import Path
from typing import Iterator, Optional
from venv import EnvBuilder as EnvBuilder

# project
import attr

# app
from .constants import PYTHONS
from .utils import cached_property, is_windows


__all__ = ['VEnvBuilder', 'VEnv', 'VEnvs']


@attr.s()
class VEnvBuilder(EnvBuilder):
    system_site_packages = attr.ib(type=bool, default=False)
    clear = attr.ib(type=bool, default=False)
    symlinks = attr.ib(type=bool, default=False)
    upgrade = attr.ib(type=bool, default=False)
    with_pip = attr.ib(type=bool, default=False)

    prompt = attr.ib(type=str, default=None)
    python = attr.ib(type=Optional[str], default=None)  # path to the python interpreter

    def ensure_directories(self, env_dir):
        context = super().ensure_directories(env_dir)
        if self.python is None:
            return context

        context.executable = self.python
        context.python_dir, context.python_exe = os.path.split(self.python)
        context.env_exe = os.path.join(context.bin_path, context.python_exe)
        return context


@attr.s()
class VEnv:
    path = attr.ib(type=Path, convert=Path)

    project = attr.ib(type=str, default=None)
    env = attr.ib(type=str, default=None)

    @property
    def name(self):
        return self.path.name

    @property
    def prompt(self) -> str:
        if self.project and self.env:
            return self.project + '/' + self.env
        if self.project:
            return self.project
        return self.path.name

    @cached_property
    def bin_path(self) -> Optional[Path]:
        if is_windows():
            path = self.path / 'Scripts'
            if path.exists():
                return path

        path = self.path / 'bin'
        if path.exists():
            return path
        return None

    @cached_property
    def lib_path(self) -> Optional[Path]:
        if is_windows():
            path = self.path / 'Lib' / 'site-packages'
            if path.exists():
                return path

        path = self.path / 'lib'
        paths = list(path.glob('python*'))
        if not paths:
            return None
        path = paths[0] / 'site-packages'
        if path.exists():
            return path
        return None

    @cached_property
    def python_path(self) -> Optional[Path]:
        if self.bin_path is None:
            return None
        for suffix in chain(PYTHONS, ['']):
            for ext in ('', '.exe'):
                path = self.bin_path / ('python' + suffix)
                if ext:
                    path = path.with_suffix(ext)
                if path.exists():
                    return path
        return None

    def exists(self) -> bool:
        """Returns true if venv already created and valid.

        It's a method like in `Path`.
        """
        return bool(self.bin_path)

    def create(self, python_path) -> None:
        builder = VEnvBuilder(
            python=str(python_path),
            with_pip=True,
            prompt=self.prompt,
        )
        builder.create(str(self.path))

        # clear cache
        if 'bin_path' in self.__dict__:
            del self.__dict__['bin_path']
        if 'python_path' in self.__dict__:
            del self.__dict__['python_path']

    def clone(self, path: Path) -> 'VEnv':
        shutil.copytree(str(self.path), str(path), copy_function=shutil.copy)
        # TODO: fix executables
        # https://github.com/ofek/hatch/blob/master/hatch/venv.py
        ...
        return type(self)(path=path)


@attr.s()
class VEnvs:
    path = attr.ib(type=Path, convert=Path)

    @cached_property
    def current(self) -> Optional[VEnv]:
        if 'VIRTUAL_ENV' in os.environ:
            return VEnv(path=os.environ['VIRTUAL_ENV'])
        # TODO: CONDA_PREFIX?
        return None

    @staticmethod
    def _encode(text: str) -> str:
        digest_bin = md5(text.encode('utf-8')).digest()
        digest_str = b64encode(digest_bin).decode()
        return digest_str.replace('+', '').replace('/', '')[:4]

    def get(self, project_path: Path, env: str) -> VEnv:
        if not project_path.exists():
            raise FileNotFoundError('Project directory does not exist')
        if not project_path.is_dir():
            raise IOError('Project path is not directory')
        formatted = str(self.path).format(
            project=project_path.name,
            digest=self._encode(str(project_path)),
            env=env,
        )
        path = Path(formatted.replace(os.path.sep + os.path.sep, os.path.sep))
        return VEnv(path=path, project=project_path.name, env=env)

    def get_by_name(self, name) -> VEnv:
        formatted = str(self.path).replace('-{digest}', '').format(project=name, digest='', env='')
        path = Path(formatted.replace(os.path.sep + os.path.sep, os.path.sep))
        return VEnv(path=path, project=name)

    def __iter__(self) -> Iterator[VEnv]:
        for path in self.path.iterdir():
            venv = VEnv(path=path)
            if venv.exists():
                yield venv

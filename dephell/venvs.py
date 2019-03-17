import os
import shutil
from base64 import b64encode
from typing import Iterator, Optional
from itertools import chain
from pathlib import Path
from hashlib import md5
from venv import EnvBuilder as EnvBuilder

import attr
from cached_property import cached_property

from .constants import PYTHONS
from .utils import is_windows


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

    @property
    def name(self):
        return self.path.name

    @cached_property
    def bin_path(self) -> Optional[Path]:
        is_win = is_windows()
        if is_win:
            path = self.path / 'Scripts'
            if path.exists():
                return path
        path = self.path / 'bin'
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
        return bool(self.bin_path)

    def create(self, python_path) -> None:
        builder = VEnvBuilder(python=str(python_path))
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
    def is_venv(self) -> bool:
        return bool({'VIRTUAL_ENV', 'CONDA_PREFIX'} & set(os.environ))

    @staticmethod
    def _encode(text: str) -> str:
        digest_bin = md5(text.encode('utf-8')).digest()
        digest_str = b64encode(digest_bin).decode()
        return digest_str.replace('+', '').replace('/', '')[:4]

    def _get_path(self, project_path: Path) -> Path:
        if not project_path.exists():
            raise FileNotFoundError('Project directory does not exist')
        if not project_path.is_dir():
            raise IOError('Project path is not directory')
        digest = self._encode(str(project_path))
        name = project_path.name + '-' + digest
        return str(self.path).format(project=name)

    def get(self, project_path: Path) -> VEnv:
        path = self._get_path(project_path)
        return VEnv(path=path)

    def __iter__(self) -> Iterator[VEnv]:
        for path in self.path.iterdir():
            venv = VEnv(path=path)
            if venv.exists():
                yield venv

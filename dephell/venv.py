from typing import Iterator, Optional
import os
import platform
from itertools import chain
from pathlib import Path
from hashlib import md5
import sys
import shutil
import subprocess

import attr
from cached_property import cached_property

from .constants import PYTHONS


def is_windows() -> bool:
    if os.name == 'nt':
        return True
    if platform.system() == 'Windows':
        return True
    return False


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
        for suffix in chain(reversed(PYTHONS), ['']):
            for ext in ('', '.exe'):
                path = self.bin_path / ('python' + suffix)
                if ext:
                    path = Path.with_suffix()
                if path.exists():
                    return path
        return None

    def exists(self) -> bool:
        return bool(self.bin_path)

    def create(self, python_path) -> int:
        command = [python_path, '-m', 'virtualenv', str(self.path)]
        result = subprocess.run(command)
        return result.returncode

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

    @cached_property
    def python_path(self) -> Path:
        return Path(sys.executable)

    def _get_path(self, project_path: Path) -> Path:
        if not project_path.exists():
            raise FileNotFoundError('Project directory does not exist')
        if not project_path.is_dir():
            raise IOError('Project path is not directory')
        digest = md5(str(project_path)).hexdigest()[:8]
        name = project_path.name + '_' + digest
        return self.path / name

    def get(self, project_path: Path) -> VEnv:
        path = self._get_path(project_path)
        return VEnv(path=path)

    def __iter__(self) -> Iterator[VEnv]:
        for path in self.path.iterdir():
            venv = VEnv(path=path)
            if venv.exists():
                yield venv

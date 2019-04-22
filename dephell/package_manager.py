# built-in
import subprocess
import sys
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, Set

# external
import attr

# app
from .converters import PIPConverter
from .models import Requirement
from .utils import cached_property


logger = getLogger('dephell')


@attr.s()
class PackageManager:
    executable = attr.ib(type=Path)
    secured = attr.ib(type=Set[str], default={'setuptools', 'pip'}, repr=False)

    # properties

    @cached_property
    def is_global(self) -> bool:
        venv_root = self.executable.parent.parent
        return not (venv_root / 'pyvenv.cfg').exists()

    # methods

    def install(self, reqs: Iterable[Requirement]) -> int:
        args = ['--no-deps']
        if self.is_global:
            args.append('--user')
        converter = PIPConverter(lock=True)
        with TemporaryDirectory() as path:
            path = Path(path) / 'requiements.txt'
            if path.exists():
                path.unlink()
            converter.dump(reqs=reqs, path=path, project=None)
            logger.debug(path.read_text())
            return self.run('install', *args, '-r', str(path))

    def remove(self, reqs: Iterable[Requirement]) -> int:
        names = [req.name for req in reqs if req.name not in self.secured]
        if not names:
            return 0
        return self.run('uninstall', '-y', *names)

    def run(self, *args) -> int:
        command_pip = [str(self.executable), '-m', 'pip'] + list(args)
        command_grep = [sys.executable, '-m', 'dephell.pip_cleaner']
        process_pip = subprocess.Popen(command_pip, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_grep = subprocess.Popen(command_grep, stdin=process_pip.stdout, stdout=sys.stdout)
        with process_pip, process_grep:
            process_pip.wait()
            process_grep.wait()

            stderr = process_pip.stderr.read().decode()
            if process_pip.returncode != 0:
                logger.error(stderr)
            elif stderr.strip():
                logger.debug(stderr)
            return process_pip.returncode

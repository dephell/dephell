# built-in
import subprocess
import sys
from argparse import ArgumentParser
from os import environ, name as os_name, pathsep
from pathlib import Path
from shutil import rmtree
from venv import create


POST_MESSAGE = """DepHell is installed now. Great!

DepHell was added in your PATH. Please, restart your shell.
"""

POST_MESSAGE_NO_MODIFY_PATH = """DepHell is installed now. Great!

Please, add DepHell's bin directory ({dephell_home_bin}) in your `PATH`
environment variable.
"""


# https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
# https://github.com/pydanny/cached-property/blob/master/cached_property.py
class cached_property(object):  # noqa: N801
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    """

    def __init__(self, func):
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class Context:
    @cached_property
    def is_windows(self) -> bool:
        if sys.platform.startswith('win'):
            return True
        if sys.platform == 'cli' and os_name == 'nt':
            return True
        return False

    @cached_property
    def dephell_name(self) -> str:
        if self.is_windows:
            return 'dephell.exe'
        return 'dephell'

    @cached_property
    def python_name(self) -> str:
        if self.is_windows:
            return 'python.exe'
        return 'python3'

    @cached_property
    def parser(self):
        parser = ArgumentParser()
        parser.add_argument('--branch', help='install dephell from git from given branch')
        parser.add_argument('--version', help='install specified version')
        parser.add_argument('--slug', default='dephell/dephell',
                            help='repository slug to use when installing from Github')
        return parser

    @cached_property
    def args(self):
        return self.parser.parse_args()

    @cached_property
    def pip_main(self):
        # install
        try:
            # external
            import pip  # noQA: F401
        except ImportError:
            print('install pip')
            # built-in
            from ensurepip import bootstrap
            bootstrap()

        # import
        try:
            # external
            from pip._internal.main import main
        except ImportError:
            try:
                # external
                from pip._internal import main
            except ImportError:
                # external
                from pip import main

        return main

    @cached_property
    def data_dir(self) -> Path:
        try:
            # external
            from appdirs import user_data_dir
        except ImportError:

            # linux
            path = Path.home() / '.local' / 'share'
            if path.exists():
                return path / 'dephell'

            # mac os
            path = Path.home() / 'Library' / 'Application Support'
            if path.exists():
                return path / 'dephell'

            self.pip_main(['install', 'appdirs'])
            # external
            from appdirs import user_data_dir

        return Path(user_data_dir('dephell'))

    @cached_property
    def venv_path(self):
        return self.data_dir / 'venvs' / 'dephell'

    @cached_property
    def python_path(self):
        """path to python in venv
        """
        pythons = self.venv_path.glob('*/{}'.format(self.python_name))
        return list(pythons)[0]

    @cached_property
    def bin_dir(self) -> Path:
        """Global directory from PATH to simlink dephell's binary
        """
        path = Path.home() / '.local' / 'bin'
        if path.exists():
            return path
        paths = [Path(path) for path in environ.get('PATH', '').split(pathsep)]
        for path in paths:
            if path.exists() and '.local' in path.parts:
                return path
        for path in paths:
            if path.exists():
                return path
        raise LookupError('cannot find place to install binary', paths)

    # actions

    def make_venv(self) -> None:
        self.pip_main  # install pip before all to have it in the venv
        if self.venv_path.exists():
            rmtree(str(self.venv_path))
        create(str(self.venv_path), with_pip=True)

    def upgrade_pip(self) -> None:
        command = [str(self.python_path), '-m', 'pip', 'install', '-U', 'pip']
        result = subprocess.run(command)
        if result.returncode != 0:
            # try again, pip is nightly
            result = subprocess.run(command)
            if result.returncode != 0:
                exit(result.returncode)

    def install_dephell(self):
        if self.args.branch:
            name = 'git+https://github.com/{slug}.git@{branch}#egg=dephell[full]'
            name = name.format(
                slug=self.args.slug,
                branch=self.args.version or self.args.branch,
            )
        elif self.args.version:
            name = 'dephell[full]=={version}'.format(version=self.args.version)
        else:
            name = 'dephell[full]'
        result = subprocess.run([str(self.python_path), '-m', 'pip', 'install', name])
        if result.returncode != 0:
            exit(result.returncode)

    def copy_binary(self):
        dephell_home_bin = self.python_path.parent
        local_path = dephell_home_bin / self.dephell_name
        if not local_path.exists():
            print('DepHell binary not found')
            exit(1)
        global_path = self.bin_dir / self.dephell_name
        if global_path.exists() or global_path.is_symlink():
            global_path.unlink()
        try:
            global_path.symlink_to(local_path)
        except OSError:
            return False
        return True


if __name__ == '__main__':
    context = Context()
    print('make venv')
    context.make_venv()
    print('upgrade pip')
    context.upgrade_pip()
    print('install dephell')
    context.install_dephell()
    print('copy binary dephell')
    modified_path = context.copy_binary()

    kwargs = {
        'dephell_home_bin': context.python_path.parent,
    }
    if modified_path:
        print(POST_MESSAGE.format(**kwargs))
    else:
        print(POST_MESSAGE_NO_MODIFY_PATH.format(**kwargs))

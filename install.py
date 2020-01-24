# built-in
import subprocess
import sys
from argparse import ArgumentParser
from os import environ, name as os_name, pathsep
from pathlib import Path
from shutil import rmtree
from typing import Tuple
from venv import create


POST_MESSAGE = """DepHell is installed now. Great!

To get started you need DepHell's bin directory ({dephell_home_bin}) in your `PATH`
environment variable. Future applications will automatically have the
correct environment, but you may need to restart your current shell.
"""

POST_MESSAGE_NO_MODIFY_PATH = """DepHell is installed now. Great!

To get started you need DepHell's bin directory ({dephell_home_bin}) in your `PATH`
environment variable. This has not been done automatically.
"""


def get_platform_names() -> Tuple[str, str]:
    """Get platform-dependent executable names"""
    windows = sys.platform.startswith('win') or (sys.platform == 'cli' and os_name == 'nt')
    names = 'dephell', 'python3'
    if windows:
        names = 'dephell.exe', 'python.exe'
    return names


# parse CLI arguments
parser = ArgumentParser()
parser.add_argument('--branch', help='install dephell from git from given branch')
parser.add_argument('--version', help='install specified version')
parser.add_argument('--slug', default='dephell/dephell',
                    help='repository slug to use when installing from Github')
args = parser.parse_args()


# install pip
try:
    import pip  # noQA: F401
except ImportError:
    print('install pip')
    from ensurepip import bootstrap
    bootstrap()


# get dephell's jail path
def get_data_dir() -> Path:
    try:
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

        try:
            from pip._internal.main import main
        except ImportError:
            try:
                from pip._internal import main
            except ImportError:
                from pip import main

        main(['install', 'appdirs'])
        from appdirs import user_data_dir

    return Path(user_data_dir('dephell'))


print('make venv')
path = get_data_dir() / 'venvs' / 'dephell'
if path.exists():
    rmtree(str(path))
create(str(path), with_pip=True)


dephell_name, python_name = get_platform_names()

print('update pip')
python_path = list(path.glob(f'*/{python_name}'))[0]
command = [str(python_path), '-m', 'pip', 'install', '-U', 'pip']
result = subprocess.run(command)
if result.returncode != 0:
    # try again, pip is nightly
    result = subprocess.run(command)
    if result.returncode != 0:
        exit(result.returncode)


print('install dephell')
if args.branch:
    name = 'git+https://github.com/{slug}.git@{branch}#egg=dephell[full]'
    name = name.format(slug=args.slug, branch=args.version or args.branch)
elif args.version:
    name = 'dephell[full]=={version}'.format(version=args.version)
else:
    name = 'dephell[full]'
result = subprocess.run([str(python_path), '-m', 'pip', 'install', name])
if result.returncode != 0:
    exit(result.returncode)


def get_bin_dir() -> Path:
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


print('copy binary dephell')
dephell_home_bin = python_path.parent
local_path = dephell_home_bin / dephell_name
if not local_path.exists():
    print('DepHell binary not found')
    exit(1)
global_path = get_bin_dir() / dephell_name
modified_path = True
if global_path.exists() or global_path.is_symlink():
    global_path.unlink()
try:
    global_path.symlink_to(local_path)
except OSError:
    modified_path = False

kwargs = {
    'dephell_home_bin': dephell_home_bin,
}
if modified_path:
    print(POST_MESSAGE.format(**kwargs))
else:
    print(POST_MESSAGE_NO_MODIFY_PATH.format(**kwargs))

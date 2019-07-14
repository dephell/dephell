# built-in
import subprocess
from argparse import ArgumentParser
from os import environ, pathsep
from pathlib import Path
from venv import create


# parse CLI arguments
parser = ArgumentParser()
parser.add_argument('--branch', help='install dephell from git from given branch')
parser.add_argument('--version', help='install specified version')
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

        path = Path.home() / '.local' / 'share'
        if path.exists():
            return path / 'dephell'

        try:
            from pip._internal import main
        except ImportError:
            from pip import main

        main(['install', 'appdirs'])
        from appdirs import user_data_dir

    return Path(user_data_dir('dephell'))


print('make venv')
path = get_data_dir() / 'venvs' / 'dephell'
create(str(path), with_pip=True)


print('update pip')
python_path = list(path.glob('*/python3'))[0]
result = subprocess.run([str(python_path), '-m', 'pip', 'install', '-U', 'pip'])
if result.returncode != 0:
    exit(result.returncode)


print('install dephell')
if args.branch:
    name = 'git+https://github.com/dephell/dephell.git@{branch}#egg=dephell[full]'
    name = name.format(branch=args.version or args.branch)
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
local_path = python_path.parent / 'dephell'
if not local_path.exists():
    print('DepHell binary not found')
    exit(1)
global_path = get_bin_dir() / 'dephell'
if global_path.exists() or global_path.is_symlink():
    global_path.unlink()
global_path.symlink_to(local_path)

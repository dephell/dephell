# built-in
import subprocess
from pathlib import Path
from typing import Optional

# external
from dephell_pythons import Python, Pythons

# app
from ..config import Config
from ..converters import CONVERTERS
from ._venv import get_venv


# https://docs.python.org/3/library/site.html
PTHS = ('easy-install.pth', 'setuptools.pth', None)
DIRS = ('site-packages', 'dist-packages')


def get_python(config: Config) -> Python:
    """Get prefered Python.

    Lookup order:

    1. Defined in config.
    2. Defined in dependencies file.
    3. Current active Python.

    Use it when you want to create new venv.
    """
    pythons = Pythons()

    # defined in config
    python = config.get('python')
    if python:
        return pythons.get_best(python)

    # defined in dependencies file
    if 'from' in config:
        loader = CONVERTERS[config['from']['format']]
        root = loader.load(path=config['from']['path'])
        if root.python:
            return pythons.get_by_spec(root.python)

    return pythons.current


def get_python_env(config: Config) -> Python:
    """
    1. Looks for venv
    2. Looks for python

    Use it when you looking for place to work with packages (list, install, remove).
    """
    venv = get_venv(config=config)
    if venv.exists():
        return venv.python
    return get_python(config=config)


def get_lib_path(python_path: Path) -> Optional[Path]:
    """Find site-packages or dist-packages dir for the given python
    """
    # get user site dir path
    user_site = None
    cmd = [str(python_path), '-c', r'print(__import__("site").USER_SITE)']
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode == 0:
        user_site = result.stdout.decode().strip()
        if user_site:
            user_site = Path(user_site)
        if not user_site.exists():
            user_site = None

    # get sys.path paths
    cmd = [str(python_path), '-c', r'print(*__import__("sys").path, sep="\n")']
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode != 0:
        return None
    paths = []
    for path in result.stdout.decode().splitlines():
        path = Path(path)
        if not path.exists():
            continue
        paths.append(path)

    # if user site dir in the sys.path, use it
    if user_site:
        for path in paths:
            if path.samefile(user_site):
                return path

    # Otherwise, lookup for site-packages or dist-packages dir.
    # Prefer a dir that is used by easy-install.
    for pth in PTHS:
        for dir_name in DIRS:
            for path in paths:
                if path.name != dir_name:
                    continue
                if pth and not (path / pth).exists():
                    continue
                return path
    return None

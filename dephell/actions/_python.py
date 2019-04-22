# external
from dephell_pythons import Python, Pythons

# app
from ..config import Config
from ..converters import CONVERTERS
from ._venv import get_venv


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

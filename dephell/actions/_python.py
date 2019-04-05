from pathlib import Path

# external
from dephell_pythons import Python, Pythons

# app
from ..converters import CONVERTERS
from ..config import Config
from ..venvs import VEnvs


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


def get_executable(config: Config) -> Path:
    """Get path to the prefered python executable.

    Lookup order:

    1. Venv for current project and env.
    2. Current active venv.
    3. Defined in config.
    4. Defined in dependencies file.
    5. Current active Python.

    Use it when you want to manipulate packages (install, list, update, remove).
    """
    venvs = VEnvs(path=config['venv'])

    # venv for current project exists
    venv = venvs.get(Path(config['project']), env=config.env)
    if venv.exists():
        return venv.python_path

    # now some venv is active
    venv = venvs.current
    if venv is not None:
        return venv.python_path

    return get_python(config=config).path

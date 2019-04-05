# external
from dephell_pythons import Python, Pythons

# app
from ..converters import CONVERTERS
from ..config import Config


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

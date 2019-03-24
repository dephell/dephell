# external
from dephell_pythons import Python, Pythons

# app
from ..converters import CONVERTERS
from ..config import Config


def get_python(config: Config) -> Python:
    pythons = Pythons()

    # defined in config
    python = config.get('python')
    if python:
        return pythons.get_best(python)

    # defined in dependency file
    loader = CONVERTERS[config['from']['format']]
    root = loader.load(path=config['from']['path'])
    if root.python:
        return pythons.get_by_spec(root.python)

    return pythons.current

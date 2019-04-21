# built-in
from pathlib import Path

# external
from dephell_venvs import VEnv, VEnvs

# app
from ..config import Config


def get_venv(config: Config) -> VEnv:
    """Get preferred venv.

    Lookup order:

    1. Venv for current project and env (if exists).
    2. Current active venv.
    3. If no active venv then venv for current project and env will be returned.

    Use it when you want to work only with virtual environment.
    """
    venvs = VEnvs(path=config['venv'])

    # venv for current project exists
    project_venv = venvs.get(Path(config['project']), env=config.env)
    if project_venv.exists():
        return project_venv

    # now some venv is active
    if venvs.current is not None:
        return venvs.current

    return project_venv

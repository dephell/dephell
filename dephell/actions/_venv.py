from pathlib import Path

# app
from ..config import Config
from ..venvs import VEnvs, VEnv


def get_venv(config: Config) -> VEnv:
    """Get preferred venv.

    Lookup order:

    1. Venv for current project and env (if exists).
    2. Current active venv.
    3. If no active venv then venv for current project and env will be returned
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

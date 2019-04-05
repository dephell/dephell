from pathlib import Path
from typing import Optional

# app
from ..config import Config
from ..venvs import VEnvs, VEnv


def get_venv(config: Config) -> Optional[VEnv]:
    """Get preferred venv.

    Lookup order:

    1. Venv for current project and env (if exists).
    2. Current active venv.
    """
    venvs = VEnvs(path=config['venv'])

    # venv for current project exists
    venv = venvs.get(Path(config['project']), env=config.env)
    if venv.exists():
        return venv

    # now some venv is active
    venv = venvs.current
    if venv is not None:
        return venv

    return None

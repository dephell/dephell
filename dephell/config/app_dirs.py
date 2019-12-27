# built-in
import os
from functools import lru_cache
from pathlib import Path

# app
from ..imports import lazy_import


appdirs = lazy_import('appdirs')


@lru_cache(maxsize=2)
def get_data_dir(app: str = 'dephell') -> Path:
    # unix
    if 'XDG_DATA_HOME' in os.environ:
        path = Path(os.environ['XDG_DATA_HOME'])
        if path.exists():
            return path / app

    # unix default
    path = Path.home() / '.local' / 'share'
    if path.exists():
        return path / app

    # mac os x
    path = Path.home() / 'Library' / 'Application Support'
    if path.exists():
        return path / app

    return Path(appdirs.user_data_dir(app))


@lru_cache(maxsize=2)
def get_cache_dir(app: str = 'dephell') -> Path:
    # unix
    if 'XDG_CACHE_HOME' in os.environ:
        path = Path(os.environ['XDG_CACHE_HOME'])
        if path.exists():
            return path / app

    # unix default
    path = Path.home() / '.cache'
    if path.exists():
        return path / app

    # mac os x
    path = Path.home() / 'Library' / 'Caches'
    if path.exists():
        return path / app

    return get_data_dir(app=app) / 'cache'

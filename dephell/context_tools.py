# built-in
import os
from contextlib import contextmanager


@contextmanager
def chdir(path):
    """Context manager for changing dir and restoring previous workdir after exit.
    """
    curdir = os.getcwd()

    path = str(path)
    if not os.path.exists(path):
        os.makedirs(path)

    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(curdir)


@contextmanager
def nullcontext(value=None):
    yield value


@contextmanager
def env_var(key, value):
    old_value = os.environ.get(key)
    os.environ[key] = value
    yield
    if old_value is None:
        del os.environ[key]
    else:
        os.environ[key] = old_value

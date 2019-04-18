# built-in
import os
import sys
from contextlib import contextmanager
from typing import Dict


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
def env_vars(vars: Dict[str, str]):
    old_vars = os.environ.copy()
    os.environ.update(vars)
    try:
        yield
    finally:
        os.environ = old_vars


@contextmanager
def override_argv(value):
    old_value = sys.argv
    sys.argv = value
    try:
        yield
    finally:
        sys.argv = old_value

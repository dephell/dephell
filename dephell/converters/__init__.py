from typing import Dict

# app
from .base import BaseConverter
from .conda import CondaConverter
from .egginfo import EggInfoConverter
from .installed import InstalledConverter
from .pip import PIPConverter
from .pipfile import PIPFileConverter
from .pipfilelock import PIPFileLockConverter
from .poetry import PoetryConverter
from .poetrylock import PoetryLockConverter
from .pyproject import PyProjectConverter
from .sdist import SDistConverter
from .setuppy import SetupPyConverter
from .wheel import WheelConverter


__all__ = [
    'CONVERTERS',

    'BaseConverter',
    'CondaConverter',
    'EggInfoConverter',
    'InstalledConverter',
    'PIPConverter',
    'PIPFileConverter',
    'PIPFileLockConverter',
    'PoetryConverter',
    'PoetryLockConverter',
    'PyProjectConverter',
    'SDistConverter',
    'SetupPyConverter',
    'WheelConverter',
]


CONVERTERS = dict(
    # archives
    egginfo=EggInfoConverter(),
    sdist=SDistConverter(),
    wheel=WheelConverter(),

    # pip
    pip=PIPConverter(lock=False),
    piplock=PIPConverter(lock=True),

    # pipenv
    pipfile=PIPFileConverter(),
    pipfilelock=PIPFileLockConverter(),

    # poetry
    poetry=PoetryConverter(),
    poetrylock=PoetryLockConverter(),

    # other
    conda=CondaConverter(),
    pyproject=PyProjectConverter(),
    setuppy=SetupPyConverter(),
    installed=InstalledConverter(),
)  # type: Dict[str, BaseConverter]

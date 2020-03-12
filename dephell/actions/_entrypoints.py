# built-in
from logging import getLogger
from typing import Iterable, Optional, Tuple

# external
from dephell_venvs import VEnv
from packaging.utils import canonicalize_name

# app
from ..constants import IS_WINDOWS
from ..converters import EggInfoConverter
from ..models import EntryPoint


logger = getLogger('dephell.actions')


def _get_matching_path(paths: Iterable, name: str) -> Optional[str]:
    name = canonicalize_name(name)
    for path in paths:
        package_name = path.stem.split('-')[0]
        if canonicalize_name(package_name) == name:
            return path
    return None


def get_entrypoints(*, venv: VEnv, name: str) -> Optional[Tuple[EntryPoint, ...]]:
    if not venv.lib_path:
        logger.critical('cannot locate lib path in the venv')
        return None
    paths = venv.lib_path.glob('*-*.*-info')
    path = _get_matching_path(paths=paths, name=name)
    if not path:
        logger.critical('cannot locate dist-info for installed package')
        return None

    path = path / 'entry_points.txt'
    if path.exists():
        return EggInfoConverter().parse_entrypoints(content=path.read_text()).entrypoints

    if not venv.bin_path:
        logger.error('cannot find any entrypoints for package')
        return None

    # entry_points.txt can be missed for egg-info.
    # In that case let's try to find a binary with the same name as package.
    names = {
        name,
        name.replace('-', '_'),
        name.replace('_', '-'),
        name.replace('-', '').replace('_', ''),

        canonicalize_name(name),
        canonicalize_name(name).replace('-', '_'),
        canonicalize_name(name).replace('_', '-'),
        canonicalize_name(name).replace('-', '').replace('_', ''),
    }
    paths = (venv.bin_path / name for name in names)
    if IS_WINDOWS:
        paths = tuple(p.with_suffix('.exe') for p in paths)

    for path in paths:
        if path.exists():
            return (EntryPoint(path=path, name=name), )
    logger.error('cannot find any entrypoints for package')
    return None

# built-in
from pathlib import Path

from .app_dirs import get_cache_dir, get_data_dir
from ..constants import DEFAULT_WAREHOUSE


DEFAULT = dict(
    tests=['tests'],
    sdist=dict(
        ratio=2,
    ),
    auth=[],

    # resolver
    prereleases=False,
    strategy='max',
    mutations=200,

    # api
    bitbucket='https://api.bitbucket.org/2.0',
    warehouse=[DEFAULT_WAREHOUSE],

    # output
    format='short',
    level='INFO',
    nocolors=False,
    silent=False,
    traceback=False,
    pdb=False,

    # venv
    venv=str(get_data_dir() / 'venvs' / '{project}-{digest}' / '{env}'),
    dotenv=str(Path('.').resolve()),

    # other
    cache=dict(
        path=str(get_cache_dir()),
        ttl=3600,
    ),
    bin=str(Path.home() / '.local' / 'bin'),
    project=str(Path('.').resolve()),
    versioning='semver',
    vendor=dict(
        path='_vendor',
        exclude=[],
    ),
)

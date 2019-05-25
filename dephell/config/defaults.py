# built-in
from pathlib import Path

from .app_dirs import get_cache_dir, get_data_dir


DEFAULT = dict(
    tests=['tests'],
    sdist=dict(
        ratio=2,
    ),

    # resolver
    prereleases=False,
    strategy='max',
    mutations=200,

    # api
    bitbucket='https://api.bitbucket.org/2.0',
    warehouse='https://pypi.org/pypi/',

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

    # cache
    cache=dict(
        path=str(get_cache_dir() / 'cache'),
        ttl=3600,
    ),

    # other
    bin=str(Path.home() / '.local' / 'bin'),
    project=str(Path('.').resolve()),
    versioning='semver',
)

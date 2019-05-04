# built-in
from pathlib import Path

# external
from appdirs import user_data_dir


data_dir = Path(user_data_dir('dephell'))


DEFAULT = dict(
    tests=['tests'],

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
    venv=str(data_dir / 'venvs' / '{project}-{digest}' / '{env}'),

    # cache
    cache=dict(
        path=str(data_dir / 'cache'),
        ttl=3600,
    ),

    # other
    bin=str(Path.home() / '.local' / 'bin'),
    project=str(Path('.').resolve()),
    versioning='semver',
)

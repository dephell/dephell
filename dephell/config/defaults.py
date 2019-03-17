# built-in
from pathlib import Path

# external
from appdirs import user_data_dir


data_dir = Path(user_data_dir('dephell'))


DEFAULT = dict(
    # resolver
    strategy='max',
    prereleases=False,

    # api
    warehouse='https://pypi.org/pypi/',
    bitbucket='https://api.bitbucket.org/2.0',

    # output
    silent=False,
    level='INFO',
    nocolors=False,
    format='short',

    # venv
    venv=str(data_dir / 'venvs' / '{project}'),

    # other
    cache=str(data_dir / 'cache'),
    project=str(Path('.').resolve()),
)

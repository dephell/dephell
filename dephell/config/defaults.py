# built-in
from pathlib import Path

# external
from appdirs import user_data_dir


data_dir = Path(user_data_dir('dephell'))


DEFAULT = dict(
    # resolver
    prereleases=False,
    strategy='max',

    # api
    bitbucket='https://api.bitbucket.org/2.0',
    warehouse='https://pypi.org/pypi/',

    # output
    format='short',
    level='INFO',
    nocolors=False,
    silent=False,
    traceback=False,

    # venv
    venv=str(data_dir / 'venvs' / '{project}'),

    # other
    cache=str(data_dir / 'cache'),
    project=str(Path('.').resolve()),
)

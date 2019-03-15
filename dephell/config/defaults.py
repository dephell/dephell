from pathlib import Path

from appdirs import user_data_dir


data_dir = Path(user_data_dir('dephell'))


DEFAULT = dict(
    # resolver
    strategy='max',

    # api
    warehouse='https://pypi.org/pypi/',
    bitbucket='https://api.bitbucket.org/2.0',

    # output
    silent=False,
    level='INFO',
    nocolors=False,

    # other
    cache=str(data_dir / 'cache'),
)

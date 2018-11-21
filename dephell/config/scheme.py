# app
from ..constants import ENVS, FORMATS


_TARGET = dict(
    type='dict',
    required=True,
    schema={
        'format': dict(
            type='string',
            required=True,
            allowed=FORMATS,
        ),
        'path': dict(
            type='string',
            required=True,
        ),
        'envs': dict(
            type='list',
            required=False,
            default=('main', 'dev'),
            allowed=ENVS,
        ),
    },
)


SCHEME = {
    'from': _TARGET,
    'to': _TARGET,
    'and': dict(
        type='list',
        schema=_TARGET,
        required=False,
        empty=True,
    ),
    'silent': dict(
        type='boolean',
        required=False,
    ),
}

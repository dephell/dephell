# app
from ..constants import ENVS, FORMATS, LOG_LEVELS, STRATEGIES


_TARGET = dict(
    type='dict',
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
    'from': dict(required=True, **_TARGET),
    # 'to': dict(required=False, **_TARGET),
    'and': dict(
        type='list',
        schema=dict(required=True, **_TARGET),
        required=False,
        empty=True,
    ),
    'silent': dict(
        type='boolean',
        required=True,  # because represented in default config
    ),
    'warehouse': dict(
        type='string',
        required=True,  # because represented in default config
    ),
    'cache': dict(
        type='string',
        required=True,  # because represented in default config
    ),
    'project': dict(
        type='string',
        required=True,  # because represented in default config
    ),
    'bitbucket': dict(
        type='string',
        required=True,  # because represented in default config
    ),
    'strategy': dict(
        type='string',
        required=True,  # because represented in default config
        allowed=STRATEGIES,
    ),
    'level': dict(
        type='string',
        required=True,  # because represented in default config
        allowed=LOG_LEVELS,
    ),
    'nocolors': dict(
        type='boolean',
        required=True,  # because represented in default config
    ),
    'venv': dict(
        type='dict',
        required=True,  # because represented in default config
        schema={
            'path': dict(
                type='string',
                required=True,
            ),
            'python': dict(
                type='string',
                required=True,
            ),
        },
    ),
}

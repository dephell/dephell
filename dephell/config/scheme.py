# app
from ..constants import FORMATS, LOG_FORMATTERS, LOG_LEVELS, REPOSITORIES, STRATEGIES


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
    },
)


# all fields with default value (defaults.py) marked as required.
SCHEME = {
    'from': dict(required=False, **_TARGET),
    'to': dict(required=False, **_TARGET),
    'and': dict(
        type='list',
        schema=_TARGET,
        required=False,
        empty=True,
    ),
    'envs': dict(
        type='list',
        required=False,
        empty=False,
    ),
    'tests': dict(
        type='list',
        required=True,
    ),

    'warehouse':    dict(type='string', required=True),
    'bitbucket':    dict(type='string', required=True),
    'repo':         dict(type='string', required=False, allowed=REPOSITORIES),

    'strategy':     dict(type='string', required=True, allowed=STRATEGIES),
    'prereleases':  dict(type='boolean', required=True),
    'mutations':    dict(type='integer', required=True),

    'silent':       dict(type='boolean', required=True),
    'level':        dict(type='string', required=True, allowed=LOG_LEVELS),
    'format':       dict(type='string', required=True, allowed=LOG_FORMATTERS),
    'nocolors':     dict(type='boolean', required=True),
    'filter':       dict(type='string', required=False),
    'traceback':    dict(type='boolean', required=True),
    'pdb':    dict(type='boolean', required=True),

    # venv
    'venv':     dict(type='string', required=True),
    'python':   dict(type='string', required=False),
    'vars': dict(
        type='dict',
        keyschema={'type': 'string'},
        valueschema={'type': 'string'},
        required=False,
    ),

    # other
    'cache': dict(
        type='dict',
        required=True,  # because represented in default config
        schema={
            'path': dict(type='string', required=True),
            'ttl': dict(type='integer', required=True),
        },
    ),
    'project':      dict(type='string', required=True),
    'bin':          dict(type='string', required=True),
    'versioning':   dict(type='string', required=True),
    'command':      dict(type='string', required=False),
}

from dephell_versioning import get_schemes

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


# + Scheme for DepHell config, validated by Cerberus:
#   https://docs.python-cerberus.org/en/stable/validation-rules.html
# + All fields with default value (defaults.py) marked as required.
# + dict() for rules, {} for content.
# + Grouped in the same groups as builders (./builders.py)
SCHEME = {
    'from':     dict(required=False, **_TARGET),
    'to':       dict(required=False, **_TARGET),
    'and':      dict(type='list', schema=_TARGET, required=False, empty=True),
    'sdist':    dict(
        type='dict',
        required=True,
        schema={'ratio': dict(type='float', required=True)},
    ),

    'auth': dict(
        type='list',
        valuesrules=dict(
            type='dict',
            schema={
                'hostname': dict(type='string', regex=r'[a-z0-9\.\-\_]'),
                'username': dict(type='string', required=True),
                'password': dict(type='string', required=True),
            },
        ),
    ),

    # api
    'warehouse':    dict(type='list', schema=dict(type='string'), required=False, empty=True),
    'bitbucket':    dict(type='string', required=True),
    'repo':         dict(type='string', required=False, allowed=REPOSITORIES),

    # resolver
    'strategy':     dict(type='string', required=True, allowed=STRATEGIES),
    'prereleases':  dict(type='boolean', required=True),
    'mutations':    dict(type='integer', required=True),

    # output
    'silent':       dict(type='boolean', required=True),
    'level':        dict(type='string', required=True, allowed=LOG_LEVELS),
    'format':       dict(type='string', required=True, allowed=LOG_FORMATTERS),
    'nocolors':     dict(type='boolean', required=True),
    'filter':       dict(type='string', required=False),
    'traceback':    dict(type='boolean', required=True),
    'pdb':          dict(type='boolean', required=True),

    # venv
    'venv':     dict(type='string', required=True),
    'dotenv':   dict(type='string', required=True),
    'python':   dict(type='string', required=False),
    'vars':     dict(
        type='dict',
        keyschema={'type': 'string'},
        valueschema={'type': 'string'},
        required=False,
    ),

    # other
    'owner':    dict(type='string', required=False),
    'tag':      dict(type='string', required=False),
    'cache':    dict(
        type='dict',
        required=True,
        schema={
            'path': dict(type='string', required=True),
            'ttl':  dict(type='integer', required=True),
        },
    ),
    'project':      dict(type='string', required=True),
    'bin':          dict(type='string', required=True),
    'envs':         dict(type='list', schema=dict(type='string'), required=False, empty=False),
    'tests':        dict(type='list', schema=dict(type='string'), required=True),
    'versioning':   dict(type='string', required=True, allowed=get_schemes()),
    'command':      dict(type='string', required=False),
    'vendor':       dict(
        type='dict',
        required=True,
        schema={
            'exclude': dict(type='list', schema=dict(type='string'), required=True, empty=True),
            'path':  dict(type='string', required=True),
        },
    ),
}

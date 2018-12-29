from types import MappingProxyType


REVERSED_OPERATIONS = MappingProxyType({
    '<':    '>',
    '<=':   '>=',
    '==':   '==',
    '===':  '===',
    '!=':   '!=',
    '>=':   '<=',
    '>':    '<',
})


VARIABLES = dict(
    python_name=(
        'implementation_name',              # 'cpython'
        'platform_python_implementation',   # 'CPython'
    ),
    python_version=(
        'implementation_version',   # '3.5.2'
        'python_full_version',      # '3.5.2'
        'python_version',           # '3.5'
    ),
    platform_name=(
        'platform_system',      # 'Linux'
        'sys_platform',         # 'linux'
        'os_name',              # 'posix'
    ),
    platform_version=(
        'platform_release',     # '4.10.0-38-generic'
        'platform_version',     # '#42~16.04.1-Ubuntu SMP Tue Oct 10 16:32:20 UTC 2017'
        'platform_machine',     # 'x86_64'
    ),
    extra=('extra', ),
)


ALIASES = {
    'os.name': 'os_name',
    'sys.platform': 'sys_platform',
    'platform.version': 'platform_version',
    'platform.machine': 'platform_machine',
    'platform.python_implementation': 'platform_python_implementation',
    'python_implementation': 'python_implementation',
}


STRING_VARIABLES = {
    'implementation_name',              # 'cpython'
    'platform_python_implementation',   # 'CPython'
    'platform_system',      # 'Linux'
    'sys_platform',         # 'linux'
    'os_name',              # 'posix'
    'platform_machine',     # 'x86_64'
}


VERSION_VARIABLES = {
    'implementation_version',   # '3.5.2'
    'python_full_version',      # '3.5.2'
    'python_version',           # '3.5'
    'platform_release',     # '4.10.0-38-generic'
    'platform_version',     # '#42~16.04.1-Ubuntu SMP Tue Oct 10 16:32:20 UTC 2017'
}

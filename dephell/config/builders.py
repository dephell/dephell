# app
from ..constants import ENVS, FORMATS, LOG_FORMATTERS, LOG_LEVELS, STRATEGIES


env_help = (
    'Pipenv has 2 envs in same file: main and dev. '
    'For poetry you can also use main-opt and dev-opt '
    'that indicates to install optional requirements '
    'from given env.'
)


def build_config(parser):
    config_group = parser.add_argument_group('Configuration file')
    config_group.add_argument('-c', '--config', help='path to config file.')
    config_group.add_argument('-e', '--env', default='main', help='environment in config.')


def build_from(parser):
    from_group = parser.add_argument_group('Input file')
    from_group.add_argument('--from', help='path or format for reading requirements.')
    from_group.add_argument('--from-format', choices=FORMATS, help='format for reading requirements.')
    from_group.add_argument('--from-path', help='path to input file.')
    from_group.add_argument('--from-env', action='append', dest='from_envs', choices=ENVS, help=env_help)


def build_to(parser):
    to_group = parser.add_argument_group('Output file')
    to_group.add_argument('--to', help='path or format for writing requirements.')
    to_group.add_argument('--to-format', choices=FORMATS, help='output requirements file format.')
    to_group.add_argument('--to-path', help='path to output file.')
    to_group.add_argument('--to-env', action='append', dest='to_envs', choices=ENVS, help=env_help)


def build_resolver(parser):
    resolver_group = parser.add_argument_group('Resolver rules')
    resolver_group.add_argument('--strategy', choices=STRATEGIES, help='Algorithm to select best release.')
    resolver_group.add_argument('--prereleases', action='store_true', help='Allow prereleases')


def build_api(parser):
    api_group = parser.add_argument_group('APIs endpoints')
    api_group.add_argument('--warehouse', help='warehouse API URL.')
    api_group.add_argument('--bitbucket', help='bitbucket API URL.')


def build_output(parser):
    output_group = parser.add_argument_group('Console output')
    output_group.add_argument('--format', choices=LOG_FORMATTERS, help='output format.')
    output_group.add_argument('--level', choices=LOG_LEVELS, help='minimal level for log messages.')

    output_group.add_argument('--nocolors', action='store_true', help='don\'t color output.')
    output_group.add_argument('--silent', action='store_true', help='suppress any output except errors.')
    output_group.add_argument('--traceback', action='store_true', help='show traceback for exceptions.')


def build_venv(parser):
    venv_group = parser.add_argument_group('Virtual environment')
    venv_group.add_argument('--venv', help='path to venv directory for project.')
    venv_group.add_argument('--python', help='python version for venv.')


def build_other(parser):
    other_group = parser.add_argument_group('Other')
    other_group.add_argument('--cache', help='path to dephell cache')
    other_group.add_argument('--project', help='path to current project')

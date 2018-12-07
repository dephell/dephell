# built-in
from argparse import ArgumentParser

# app
from ..constants import ENVS, FORMATS


__all__ = ['parser']


parser = ArgumentParser(
    description='Lock and convert dependencies between formats.',
)

env_help = (
    'Pipenv has 2 envs in same file: main and dev. '
    'For poetry you can also use main-opt and dev-opt '
    'that indicates to install optional requirements '
    'from given env.'
)

config_group = parser.add_argument_group('Configuration file')
config_group.add_argument('-c', '--config', help='path to config file')
config_group.add_argument('-e', '--env', default='main', help='environment')

from_group = parser.add_argument_group('Input file')
from_group.add_argument('--from-format', choices=FORMATS, help='format for reading requirements')
from_group.add_argument('--from-path', help='path to input file')
from_group.add_argument('--from-env', action='append', dest='from_envs', choices=ENVS, help=env_help)

to_group = parser.add_argument_group('Output file')
to_group.add_argument('--to-format', choices=FORMATS, help='output requirements file format')
to_group.add_argument('--to-path', help='path to output file')
to_group.add_argument('--to-env', action='append', dest='to_envs', choices=ENVS, help=env_help)

api_group = parser.add_argument_group('APIs endpoints')
api_group.add_argument('--warehouse', help='warehouse API URL.')
api_group.add_argument('--bitbucket', help='bitbucket API URL')

output_group = parser.add_argument_group('Console output')
output_group.add_argument('--silent', action='store_true', help='suppress any output except errors.')

other_group = parser.add_argument_group('other')
other_group.add_argument('--cache', help='path to dephell cache')

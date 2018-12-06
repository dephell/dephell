# built-in
from argparse import ArgumentParser

# app
from ..constants import ENVS, FORMATS


parser = ArgumentParser(
    description='Lock and convert dependencies between formats.',
)

env_help = (
    'Pipenv has 2 envs in same file: main and dev. '
    'For poetry you can also use main-opt and dev-opt '
    'that indicates to install optional requirements '
    'from given env.'
)

# config
parser.add_argument('-c', '--config', help='path to config file')
parser.add_argument('-e', '--env', default='main', help='environment')

# from
parser.add_argument('--from-format', choices=FORMATS, help='format for reading requirements')
parser.add_argument('--from-path', help='path to input file')
parser.add_argument('--from-env', action='append', dest='from_envs', choices=ENVS, help=env_help)

# to
parser.add_argument('--to-format', choices=FORMATS, help='output requirements file format')
parser.add_argument('--to-path', help='path to output file')
parser.add_argument('--to-env', action='append', dest='to_envs', choices=ENVS, help=env_help)

# APIs
parser.add_argument('--warehouse', help='warehouse API URL.')
parser.add_argument('--bitbucket', help='bitbucket API URL')

# other
parser.add_argument('--silent', action='store_true', help='suppress any output except errors.')
parser.add_argument('--cache', help='path to dephell cache')

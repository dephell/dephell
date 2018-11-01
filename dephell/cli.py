from argparse import ArgumentParser
from .commands import commands


parser = ArgumentParser(
    description='Lock and convert dependencies between formats.',
)
parser.add_argument('command', choices=commands.keys(), help='command to execute')


def main(argv):
    args = parser.parse_args(argv)
    if args.command is None:
        parser.parse_args('--help')

    command = commands[args.command]
    args = command.parser(argv[1:])
    task = command(args)
    result = task()
    return int(not result)

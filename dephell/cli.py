from argparse import ArgumentParser
from .commands import commands


parser = ArgumentParser(
    description='Lock and convert dependencies between formats.',
)
parser.add_argument('command', choices=commands.keys(), help='command to execute')


def main(argv):
    args = parser.parse_args(argv[:1])
    if args.command is None:
        parser.parse_args('--help')
    command = commands[args.command]
    task = command(argv[1:])

    is_valid = task.validate()
    if not is_valid:
        return 2

    result = task()
    return int(not result)

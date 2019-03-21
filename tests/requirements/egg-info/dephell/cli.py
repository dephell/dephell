# built-in
from argparse import ArgumentParser

# app
from .commands import commands
from .constants import ReturnCodes


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
        return ReturnCodes.INVALID_CONFIG.value

    result = task()
    if not result:
        return ReturnCodes.COMMAND_ERROR.value
    return ReturnCodes.OK.value

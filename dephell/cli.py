# built-in
from logging import getLogger
from pdb import post_mortem
from sys import argv
from typing import List

# external
from dephell_argparse import Command, Parser

# app
from .commands import COMMANDS
from .constants import ReturnCodes
from .exceptions import ExtraException


logger = getLogger('dephell.cli')
parser = Parser(
    description='Manage dependencies, projects, virtual environments.',
    usage='dephell COMMAND [OPTIONS]',
)
for handler in COMMANDS.values():
    parser.add_command(handler=handler)


def main(argv: List[str]) -> int:
    # print help
    if not argv:
        parser._print_message(parser.format_help())
        return ReturnCodes.OK.value
    if len(argv) == 1 and argv[0] in ('--help', '-h', 'help', 'commands'):
        parser._print_message(parser.format_help())
        return ReturnCodes.OK.value
    if len(argv) == 1 and argv[0] in ('-v', '--version'):
        argv = ['inspect', 'self']

    # rewrite argv to get help about command
    if len(argv) >= 1 and argv[0] in ('--help', '-h', 'help'):
        argv = list(argv[1:]) + ['--help']

    # get command
    handler = parser.get_command(argv=argv)
    if not handler:
        command = Command(argv=argv, commands=parser._handlers.keys())
        parser._print_message(parser.format_help(command=command))
        return ReturnCodes.UNKNOWN_COMMAND.value

    # parse config
    try:
        handler.config
    except KeyError as e:  # env not found
        logger.exception(e.args[0])
        return ReturnCodes.INVALID_CONFIG.value
    except Exception as e:
        logger.exception('{}: {}'.format(type(e).__name__, e))
        if '--traceback' in argv:
            raise
        return ReturnCodes.UNKNOWN_EXCEPTION.value

    # validate config
    is_valid = handler.validate()
    if not is_valid:
        return ReturnCodes.INVALID_CONFIG.value

    # execute command
    try:
        result = handler()
    except Exception as exc:
        if isinstance(exc, ExtraException):
            logger.exception(str(exc), extra=exc.extra)
        else:
            logger.exception('{}: {}'.format(type(exc).__name__, exc))
        if hasattr(handler, 'config') and handler.config.get('pdb', False):
            post_mortem()
        return ReturnCodes.UNKNOWN_EXCEPTION.value
    except KeyboardInterrupt:
        logger.exception('stopped by user')
        return ReturnCodes.UNKNOWN_EXCEPTION.value
    if not result:
        return ReturnCodes.COMMAND_ERROR.value
    return ReturnCodes.OK.value


def entrypoint():
    exit(main(argv[1:]))

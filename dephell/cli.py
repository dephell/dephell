# built-in
from argparse import Action, ArgumentParser
from logging import getLogger
from pdb import post_mortem
from sys import argv
from typing import List

# app
from .commands import commands
from .constants import ReturnCodes


logger = getLogger('dephell.cli')


class PatchedParser(ArgumentParser):
    def format_help(self):
        formatter = self._get_formatter()
        formatter.add_usage(self.usage, self._actions, self._mutually_exclusive_groups)
        formatter.add_text(self.description)

        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
        formatter.add_text(self.epilog)

        formatter.start_section('commands')
        for name, command in sorted(commands.items()):
            descr = command.get_parser().description.split('\n')[0]
            formatter.add_argument(Action([name], '', help=descr))
        formatter.end_section()

        return formatter.format_help()


parser = PatchedParser(
    description='Manage dependencies, projects, virtual environments.',
)
parser.add_argument('command', choices=commands.keys(), nargs='?', help='command to execute')


def main(argv: List[str]) -> int:
    # get command name
    for size, direction in ((1, 1), (2, 1), (2, -1)):
        command_name = ' '.join(argv[:size][::direction])
        command_args = argv[size:]
        if command_name in commands:
            break
    else:
        args = parser.parse_args(argv[:1])
        if args.command is None:
            parser.parse_args(['--help'])
        command_name = args.command
        command_args = argv[1:]

    # get and init command object
    command = commands[command_name]
    try:
        task = command(command_args)
    except KeyError as e:  # env not found
        logger.exception(e.args[0])
        return ReturnCodes.INVALID_CONFIG.value
    except Exception as e:
        logger.exception('{}: {}'.format(type(e).__name__, e))
        return ReturnCodes.UNKNOWN_EXCEPTION.value

    # validate config
    is_valid = task.validate()
    if not is_valid:
        return ReturnCodes.INVALID_CONFIG.value

    # execute command
    try:
        result = task()
    except Exception as e:
        logger.exception('{}: {}'.format(type(e).__name__, e))
        if hasattr(task, 'config') and task.config.get('pdb', False):
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

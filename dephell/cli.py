# built-in
from argparse import Action, ArgumentParser
from collections import Counter, defaultdict
from logging import getLogger
from pdb import post_mortem
from sys import argv
from typing import List, Optional, Tuple

# app
from .commands import COMMANDS
from .constants import ReturnCodes
from .exceptions import ExtraException


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
        for name, command in sorted(COMMANDS.items()):
            descr = command.get_parser().description.split('\n')[0]
            formatter.add_argument(Action([name], '', help=descr))
        formatter.end_section()

        return formatter.format_help()


parser = PatchedParser(
    description='Manage dependencies, projects, virtual environments.',
    usage='dephell COMMAND [OPTIONS]',
)
parser.add_argument('command', choices=COMMANDS.keys(), nargs='?', help='command to execute')


def commands_are_similar(command1: str, command2: str) -> bool:
    given = Counter(command1)
    guess = Counter(command2)
    counter_diff = (given - guess) + (guess - given)
    diff = sum(counter_diff.values())
    return diff <= 1


def get_command_name_and_size(argv: List[str], commands=COMMANDS) -> Optional[Tuple[str, int]]:
    if not argv:
        return None

    for size, direction in ((1, 1), (2, 1), (2, -1)):
        command_name = ' '.join(argv[:size][::direction])
        if command_name in commands:
            return command_name, size

    # specified the only one word from command
    commands_by_parts = defaultdict(list)
    for command_name in commands:
        for part in command_name.split():
            commands_by_parts[part].append(command_name)
    command_names = commands_by_parts[argv[0]]
    if len(command_names) == 1:
        return command_names[0], 1

    # typo in command name
    for size in 1, 2:
        command_specified = ' '.join(argv[:size])
        for command_guess in commands:
            if commands_are_similar(command_specified, command_guess):
                return command_guess, size

    return None


def main(argv: List[str]) -> int:
    if not argv or argv[0] in ('--help', 'help', 'commands'):
        parser.parse_args(['--help'])

    name_and_size = get_command_name_and_size(argv=argv)
    if name_and_size:
        command_name = name_and_size[0]
        command_args = argv[name_and_size[1]:]
    else:
        logger.error('ERROR: Unknown command')
        parser.parse_args(['--help'])

    # get and init command object
    command = COMMANDS[command_name]
    try:
        task = command(command_args)
    except KeyError as e:  # env not found
        logger.exception(e.args[0])
        return ReturnCodes.INVALID_CONFIG.value
    except Exception as e:
        logger.exception('{}: {}'.format(type(e).__name__, e))
        if '--traceback' in argv:
            raise
        return ReturnCodes.UNKNOWN_EXCEPTION.value

    # validate config
    is_valid = task.validate()
    if not is_valid:
        return ReturnCodes.INVALID_CONFIG.value

    # execute command
    try:
        result = task()
    except Exception as exc:
        if isinstance(exc, ExtraException):
            logger.exception(str(exc), extra=exc.extra)
        else:
            logger.exception('{}: {}'.format(type(exc).__name__, exc))
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

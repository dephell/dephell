# built-in
from argparse import Action, ArgumentParser
from collections import Counter, defaultdict
from logging import getLogger
from pdb import post_mortem
from sys import argv
from typing import List, Optional, Set, Tuple

# app
from .commands import COMMANDS
from .constants import ReturnCodes
from .exceptions import ExtraException
from .logging_helpers import Fore


logger = getLogger('dephell.cli')


class PatchedParser(ArgumentParser):
    def format_help(self):
        formatter = self._get_formatter()
        formatter.add_usage(self.usage, self._actions, self._mutually_exclusive_groups)
        formatter.add_text(self.description)

        for action_group in self._action_groups:
            formatter.start_section(Fore.YELLOW + action_group.title + Fore.RESET)
            formatter.add_text(action_group.description)

            # do not show all commands in a row, just say that command goes here
            if action_group.title == 'positional arguments':
                action_group._group_actions[0].choices = {'command_name'}

            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
        formatter.add_text(self.epilog)
        self._format_commands(formatter=formatter)
        return formatter.format_help()

    def _get_formatter(self):
        formatter = super()._get_formatter()
        formatter._action_max_length = 36
        formatter._max_help_position = 36
        formatter._width = 120
        return formatter

    def _format_commands(self, formatter, section_name: str = 'commands',
                         guesses: Set[str] = None) -> None:
        formatter.start_section(Fore.YELLOW + section_name + Fore.RESET)
        prev_group = ''
        colors = {True: Fore.GREEN, False: Fore.BLUE}
        color = True
        for name, command in sorted(COMMANDS.items()):
            if guesses and name not in guesses:
                continue

            # switch colors for every group
            group, _, subname = name.rpartition(' ')
            if group != prev_group:
                prev_group = group
                color = not color

            descr = command.get_parser().description.split('\n')[0]
            formatter.add_argument(Action(
                option_strings=[colors[color] + name + Fore.RESET],
                dest='',
                help=descr,
            ))
        formatter.end_section()

    def format_guesses(self, argv: List[str], commands=COMMANDS):
        given = argv[0]
        guesses = set()
        for command_name in commands:
            group_name = command_name.split()[0]
            if group_name == given:
                guesses.add(command_name)

        formatter = self._get_formatter()
        formatter.add_text(Fore.RED + 'ERROR:' + Fore.RESET + ' unknown command')
        self._format_commands(
            formatter=formatter,
            section_name='possible commands',
            guesses=guesses,
        )
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
        text = parser.format_guesses(argv=argv)
        print(text)
        return 1

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

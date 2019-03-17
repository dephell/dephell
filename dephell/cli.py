# built-in
from argparse import Action, ArgumentParser

# app
from .commands import commands
from .constants import ReturnCodes


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
    description='Lock and convert dependencies between formats.',
)
parser.add_argument('command', choices=commands.keys(), nargs='?', help='command to execute')


def main(argv):
    args = parser.parse_args(argv[:1])
    if args.command is None:
        parser.parse_args(['--help'])
    command = commands[args.command]
    task = command(argv[1:])

    is_valid = task.validate()
    if not is_valid:
        return ReturnCodes.INVALID_CONFIG.value

    result = task()
    if not result:
        return ReturnCodes.COMMAND_ERROR.value
    return ReturnCodes.OK.value

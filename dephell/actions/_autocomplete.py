# built-in
from collections import defaultdict

# external
from jinja2 import Environment, PackageLoader


templates = Environment(
    loader=PackageLoader('dephell', 'templates'),
)


PATHS = (
    'from', 'from_path',
    'to', 'to_path',
    'config', 'project',
    'venv', 'bin',
    'cache_path',
)


def make_bash_autocomplete() -> str:
    from ..commands import commands

    template = templates.get_template('autocomplete.sh.j2')
    tree = defaultdict(set)
    first_words = set()
    for command in commands:
        command, _sep, subcommand = command.partition(' ')
        first_words.add(command)
        if subcommand:
            tree[command].add(subcommand)

    arguments = defaultdict(set)
    for command_name, command in commands.items():
        for action in command.get_parser()._actions:
            arguments[command_name].update(action.option_strings)

    return template.render(first_words=first_words, tree=tree, arguments=arguments)


def make_zsh_autocomplete() -> str:
    from ..commands import commands

    template = templates.get_template('autocomplete-zsh.sh.j2')
    tree = defaultdict(set)
    first_words = set()
    for command_name, command in commands.items():
        command_name, _sep, subcommand = command_name.partition(' ')
        first_words.add(command_name)
        if subcommand:
            description = command.get_parser().description.lstrip().split('\n', maxsplit=1)[0]
            tree[command_name].add((subcommand, description))

    arguments = defaultdict(list)
    for command_name, command in commands.items():
        for action in command.get_parser()._actions:
            if action.help:
                arguments[command_name].append(dict(
                    opts=action.option_strings,
                    choices=action.choices and ' '.join(action.choices),
                    help=action.help,
                    dest=action.dest,
                    files=action.dest in PATHS,
                ))

    script = template.render(first_words=first_words, tree=tree, arguments=arguments)

    while ' \n' in script:
        script = script.replace(' \n', '\n')
    while '\n\n' in script:
        script = script.replace('\n\n', '\n')
    return script

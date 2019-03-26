# built-in
from argparse import ArgumentParser
from collections import defaultdict

from jinja2 import Environment, PackageLoader

# app
from ..config import builders
from .base import BaseCommand


env = Environment(
    loader=PackageLoader('dephell', 'templates'),
)


DUMPERS = (
    ('setuppy', 'setup.py'),
    ('egginfo', '.'),
    ('sdist', 'dist/'),
    ('wheel', 'dist/'),
)


class AutocompleteCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell autocomplete',
            description='Enable dephell commands autocomplete for current shell',
        )
        builders.build_config(parser)
        builders.build_output(parser)
        return parser

    def __call__(self):
        from . import commands

        template = env.get_template('autocomplete.sh.j2')
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

        script = template.render(first_words=first_words, tree=tree, arguments=arguments)
        print(script)

        return True

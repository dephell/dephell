# built-in
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path

from appdirs import user_data_dir
from dephell_shells import Shells
from jinja2 import Environment, PackageLoader

# app
from ..config import builders
from .base import BaseCommand


env = Environment(
    loader=PackageLoader('dephell', 'templates'),
)


class AutocompleteCommand(BaseCommand):
    """Enable DepHell commands autocomplete for current shell.

    https://dephell.readthedocs.io/en/latest/cmd-autocomplete.html
    """

    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell autocomplete',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        return parser

    def __call__(self):
        shell = Shells(bin_path=None).shell_name
        msg = 'Autocompletion installed. Please, reload your shell'

        if shell == 'bash':
            self._bash()
            self.logger.info(msg)
            return True

        if shell == 'zsh':
            self._zsh()
            self.logger.info(msg)
            return True

        self.logger.error('unsupported shell', extra=dict(shell=shell))
        return False

    def _bash(self):
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
        path = Path.home() / '.local' / 'etc' / 'bash_completion.d' / 'dephell.bash-completion'
        path.write_text(script)

        for rc_name in ('.bashrc', '.profile'):
            rc_path = Path.home() / rc_name
            if not rc_path.exists():
                continue
            if 'bash_completion.d' not in rc_path.read_text():
                with rc_path.open('a') as stream:
                    stream.write('\n\nsource {}\n'.format(str(path)))
            break

    def _zsh(self):
        from . import commands

        template = env.get_template('autocomplete-zsh.sh.j2')
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
                    arguments[command_name].append((action.option_strings, action.help))

        script = template.render(first_words=first_words, tree=tree, arguments=arguments)
        path = Path(user_data_dir('dephell')) / '_dephell_zsh_autocomplete'
        path.write_text(script)
        path.chmod(0o777)

        rc_path = Path.home() / '.zshrc'
        if str(path) not in rc_path.read_text():
            with rc_path.open('a') as stream:
                stream.write('\n\nsource {}\n'.format(str(path)))

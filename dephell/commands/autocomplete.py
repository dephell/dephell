# built-in
from argparse import ArgumentParser
from pathlib import Path
from platform import platform

# external
from appdirs import user_data_dir
from dephell_shells import Shells

# app
from ..actions import make_bash_autocomplete, make_zsh_autocomplete
from ..config import builders
from .base import BaseCommand


class AutocompleteCommand(BaseCommand):
    """Enable DepHell commands autocomplete for current shell.

    https://dephell.readthedocs.io/en/latest/cmd-autocomplete.html
    """

    @classmethod
    def get_parser(cls) -> ArgumentParser:
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
        script = make_bash_autocomplete()

        # https://github.com/dephell/dephell/pull/62
        path = Path.home() / '.local' / 'etc' / 'bash_completion.d' / 'dephell.bash-completion'
        if platform().lower() == 'darwin':
            # ref. https://itnext.io/programmable-completion-for-bash-on-macos-f81a0103080b
            path = Path('/') / 'usr' / 'local' / 'etc' / 'bash_completion.d' / 'dephell.bash-completion'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(script)

        for rc_name in ('.bashrc', '.profile', '.bash_profile'):
            rc_path = Path.home() / rc_name
            if not rc_path.exists():
                continue
            if 'bash_completion.d' not in rc_path.read_text():
                with rc_path.open('a') as stream:
                    stream.write('\n\nsource {}\n'.format(str(path)))
            break

    def _zsh(self):
        script = make_zsh_autocomplete()
        path = Path(user_data_dir('dephell')) / '_dephell_zsh_autocomplete'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(script)
        path.chmod(0o777)

        rc_path = Path.home() / '.zshrc'
        if str(path) not in rc_path.read_text():
            with rc_path.open('a') as stream:
                stream.write('\n\nsource {}\n'.format(str(path)))

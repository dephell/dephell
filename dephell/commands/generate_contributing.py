# built-in
from argparse import ArgumentParser
from pathlib import Path

# external
import tomlkit

# app
from ..actions import make_contributing
from ..config import builders
from .base import BaseCommand


class GenerateContributingCommand(BaseCommand):
    """Create CONTRIBUTING.md for DepHell-based project.

    https://dephell.readthedocs.io/en/latest/cmd-generate-contributing.html
    """
    COMMAND_TITLE = 'CONTRIBUTING.md'

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell generate contributing',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        if self.args.config:
            path = Path(self.args.config)
        else:
            path = Path(self.config['project']) / 'pyproject.toml'
            if not path.exists():
                self.logger.error('cannot generate {} without config'.format(self.COMMAND_TITLE))
                return False

        with path.open('r', encoding='utf8') as stream:
            config = tomlkit.parse(stream.read())
        config = dict(config['tool']['dephell'])
        project_path = Path(self.config['project'])
        text = make_contributing(config=config)
        (project_path / self.COMMAND_TITLE).write_text(text)
        self.logger.info('{} generated'.format(self.COMMAND_TITLE))
        return True

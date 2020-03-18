# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..actions import make_editorconfig
from ..config import builders
from .base import BaseCommand


class GenerateEditorconfigCommand(BaseCommand):
    """Create EditorConfig for project.
    https://editorconfig.org/
    """
    # because we don't actually use anything from the config
    find_config = False

    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        project_path = Path(self.config['project'])
        text = make_editorconfig(path=project_path)
        (project_path / '.editorconfig').write_text(text)
        self.logger.info('editorconfig generated')
        return True

# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..actions import make_editorconfig
from ..config import builders
from .base import BaseCommand


class GenerateEditorconfigCommand(BaseCommand):
    """Create EditorConfig for project.

    https://dephell.readthedocs.io/en/latest/cmd-generate-editorconfig.html
    https://editorconfig.org/
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell generate editorconfig',
            description=cls.__doc__,
        )
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

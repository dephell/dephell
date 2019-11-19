# built-in
from argparse import ArgumentParser
from pathlib import Path
from shutil import rmtree

# app
from ..actions import format_size, get_path_size
from ..config import builders
from .base import BaseCommand


class SelfUncacheCommand(BaseCommand):
    """Remove dephell cache.
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        path = Path(self.config['cache']['path'])
        if path.exists():
            size = format_size(get_path_size(path))
            rmtree(str(path))
            self.logger.info('cache removed', extra=dict(size=size))
        else:
            self.logger.warning('no cache found')
        return True

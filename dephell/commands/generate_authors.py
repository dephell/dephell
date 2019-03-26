# built-in
import subprocess
from argparse import ArgumentParser, REMAINDER
from pathlib import Path

# app
from ..config import builders
from .base import BaseCommand


class GenerateAuthorsCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell generate authors',
            description='Create AUTHORS file for project by git log',
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=REMAINDER, help='package to install')
        return parser

    def __call__(self):
        result = subprocess.run(['git', 'log', '--pretty="%ae|%an%n%ce|%cn"'], capture_output=True)
        authors = dict()
        for line in result.stdout.decode().strip().split('\n'):
            mail, name = line.split('|')
            mail = mail.strip().replace('"', '')
            name = name.strip().replace('"', '')
            authors[mail] = name
        text = '\n'.join('{} <{}>'.format(name, mail) for mail, name in authors.items())
        Path('AUTHORS').write_text(text)
        self.logger.info('AUTHORS generated')
        return True

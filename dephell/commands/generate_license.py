# built-in
from argparse import ArgumentParser
from datetime import datetime
from getpass import getuser
from pathlib import Path

# external
from dephell_licenses import licenses

# app
from ..config import builders
from .base import BaseCommand


class GenerateLicenseCommand(BaseCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell generate license',
            description='Create LICENSE file',
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs=1, help='licnse name')
        return parser

    def __call__(self):
        name = ' '.join(self.args.name)
        license = licenses.get_by_id(name)
        if license is None:
            license = licenses.get_by_name(name)
        if license is None:
            self.logger.error('cannot find license with given name')
            return False
        text = license.make_text(copyright='{year} {name}'.format(
            year=datetime.now().year,
            name=getuser().title(),
        ))
        Path('LICENSE').write_text(text)
        self.logger.info('license generated', extra=dict(license=license.name))
        return True

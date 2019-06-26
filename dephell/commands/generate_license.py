# built-in
from argparse import REMAINDER, ArgumentParser
from datetime import datetime
from getpass import getuser
from pathlib import Path

# external
from dephell_licenses import licenses
from dephell_discover import Root as PackageRoot

# app
from ..config import builders
from ..converters import CONVERTERS
from .base import BaseCommand


class GenerateLicenseCommand(BaseCommand):
    """Create LICENSE file.

    https://dephell.readthedocs.io/cmd-generate-license.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell generate license',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('--owner', help='name of the owner')
        parser.add_argument('name', nargs=REMAINDER, help='license name')
        return parser

    def __call__(self) -> bool:
        # get license object
        name = ' '.join(self.args.name).strip()
        if not name:
            name = 'MIT'
        license = licenses.get_by_id(name)
        if license is None:
            license = licenses.get_by_name(name)
        if license is None:
            self.logger.error('cannot find license with given name')
            return False

        # author name from --owner
        author = self.config.get('owner')

        # get author from `from`
        if not author and 'from' in self.config:
            loader = CONVERTERS[self.config['from']['format']]
            root = loader.load(self.config['from']['path'])
            if root.authors:
                author = root.authors[0]

        # author from project config file
        if not author:
            metainfo = PackageRoot(Path(self.config['project'])).metainfo
            if metainfo and metainfo.authors:
                author = metainfo.authors[0]

        # author from getuser().title
        if not author:
            author = getuser().title()

        # generate license text
        text = license.make_text(copyright='{year} {name}'.format(
            year=datetime.now().year,
            name=author,
        ))
        (Path(self.config['project']) / 'LICENSE').write_text(text)
        self.logger.info('license generated', extra=dict(license=license.name))
        return True

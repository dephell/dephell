# built-in
import os.path
from logging import getLogger

# app
from ..config import config, parser


logger = getLogger(__name__)


class BaseCommand:
    parser = parser

    def __init__(self, argv):
        parser = self.get_parser()
        self.args = parser.parse_args(argv)
        self.config = self.get_config(self.args)

    @classmethod
    def get_parser(cls):
        return cls.parser

    @classmethod
    def get_config(cls, args):
        config.setup_logging()
        if args.config:
            config.attach_file(path=args.config, env=args.env)
        elif os.path.exists('pyproject.toml'):
            config.attach_file(path='pyproject.toml', env=args.env)
        else:
            logger.warning('cannot find config file')
        config.attach_cli(args)
        config.setup_logging()
        return config

    def validate(self):
        is_valid = self.config.validate()
        if not is_valid:
            print(self.config.format_errors())
        return is_valid

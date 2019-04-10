# built-in
import os.path
from argparse import ArgumentParser
from logging import getLogger

# app
from ..config import Config, config


class BaseCommand:
    logger = getLogger('dephell.commands')

    def __init__(self, argv, config: Config = None):
        parser = self.get_parser()
        self.args = parser.parse_args(argv)

        if config is None:
            self.config = self.get_config(self.args)
        else:
            self.config = config

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        raise NotImplementedError

    @classmethod
    def get_config(cls, args) -> Config:
        config.setup_logging()
        if args.config:
            config.attach_file(path=args.config, env=args.env)
        elif os.path.exists('pyproject.toml'):
            data = config.attach_file(path='pyproject.toml', env=args.env, silent=True)
            if data is None:
                cls.logger.warning('cannot find tool.dephell section in the config')
        else:
            cls.logger.warning('cannot find config file')
        config.attach_cli(args)
        config.setup_logging()
        return config

    def validate(self) -> bool:
        is_valid = self.config.validate()
        if not is_valid:
            self.logger.error('invalid config')
            print(self.config.format_errors())
        return is_valid

    def __call__(self) -> bool:
        raise NotImplementedError

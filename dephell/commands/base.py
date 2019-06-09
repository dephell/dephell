# built-in
import os.path
from argparse import ArgumentParser
from logging import getLogger

# external
import tomlkit

# app
from ..config import Config, config, get_data_dir
from ..constants import CONFIG_NAMES, GLOBAL_CONFIG_NAME


class BaseCommand:
    logger = getLogger('dephell.commands')

    def __init__(self, argv, config: Config = None):
        parser = self.get_parser()
        self.args = parser.parse_args(argv)
        self.config = self.get_config(self.args) if config is None else config

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        raise NotImplementedError

    @classmethod
    def get_config(cls, args) -> Config:
        config.setup_logging()
        cls._attach_global_config_file()
        cls._attach_config_file(path=args.config, env=args.env)
        config.attach_cli(args)
        config.setup_logging()
        return config

    @classmethod
    def _attach_global_config_file(cls) -> bool:
        global_config = get_data_dir() / GLOBAL_CONFIG_NAME
        if not global_config.exists():
            return False
        content = global_config.read_text(encoding='utf8')
        doc = tomlkit.parse(content)
        config.attach(data=dict(doc))
        return True

    @classmethod
    def _attach_config_file(cls, path, env) -> bool:
        if path:
            config.attach_file(path=path, env=env)
            return True

        for path in CONFIG_NAMES:
            if not os.path.exists(path):
                continue
            data = config.attach_file(path=path, env=env, silent=True)
            if data is None:
                cls.logger.warning('cannot find tool.dephell section in the config', extra=dict(
                    path=path,
                ))
                return False
            return True

        cls.logger.warning('cannot find config file')
        return False

    def validate(self) -> bool:
        is_valid = self.config.validate()
        if not is_valid:
            self.logger.error('invalid config')
            print(self.config.format_errors())
        return is_valid

    def __call__(self) -> bool:
        raise NotImplementedError

# built-in
import os.path
from argparse import ArgumentParser
from pathlib import Path
from logging import getLogger
from typing import Dict, Set

# external
import tomlkit

# app
from ..actions import attach_deps, get_python_env
from ..controllers import analyze_conflict
from ..converters import CONVERTERS, InstalledConverter
from ..config import Config, config, get_data_dir
from ..constants import CONFIG_NAMES, GLOBAL_CONFIG_NAME


class BaseCommand:
    logger = getLogger('dephell.commands')

    def __init__(self, argv, config: Config = None):
        parser = self.get_parser()
        self.args = parser.parse_args(argv)
        self.config = self.get_config(self.args) if config is None else config

    # builders

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

    def validate(self) -> bool:
        is_valid = self.config.validate()
        if not is_valid:
            self.logger.error('invalid config')
            print(self.config.format_errors())
        return is_valid

    # interface

    def __call__(self) -> bool:
        raise NotImplementedError

    # helpers

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

    def _get_locked(self, default_envs: Set[str] = None):
        if 'from' not in self.config:
            python = get_python_env(config=self.config)
            self.logger.debug('choosen python', extra=dict(path=str(python.path)))
            resolver = InstalledConverter().load_resolver(paths=python.lib_paths)
            return self._resolve(resolver=resolver, default_envs=default_envs)

        loader_config = self._get_loader_config_for_lockfile()
        if not Path(loader_config['path']).exists():
            self.error('cannot find dependency file', extra=dict(path=loader_config['path']))
            return None

        self.logger.info('get dependencies', extra=dict(
            format=loader_config['format'],
            path=loader_config['path'],
        ))
        loader = CONVERTERS[loader_config['format']]
        resolver = loader.load_resolver(path=loader_config['path'])
        attach_deps(resolver=resolver, config=self.config, merge=False)
        return self._resolve(resolver=resolver, default_envs=default_envs)

    def _resolve(self, resolver, default_envs: Set[str] = None):
        # resolve
        if len(resolver.graph._layers) <= 1:  # if it isn't resolved yet
            self.logger.info('build dependencies graph...')
            resolved = resolver.resolve(silent=self.config['silent'])
            if not resolved:
                conflict = analyze_conflict(resolver=resolver)
                self.logger.warning('conflict was found')
                print(conflict)
                return None

        # apply envs if needed
        if 'envs' in self.config:
            resolver.apply_envs(set(self.config['envs']))
        elif default_envs:
            resolver.apply_envs(default_envs)

        return resolver

    def _get_loader_config_for_lockfile(self) -> Dict[str, str]:
        # if path specified in CLI, use it
        if set(self.args.__dict__) & {'from', 'from_format', 'from_path'}:
            return self.config['from']

        dumper_config = self.config.get('to')
        if not dumper_config or dumper_config == 'stdout':
            return self.config['from']

        if not Path(dumper_config['path']).exists():
            return self.config['from']

        dumper = CONVERTERS[dumper_config['format']]
        if dumper.lock:
            return dumper_config

        return self.config['from']

# built-in
import os.path
import re
from logging import getLogger
from os import environ
from pathlib import Path
from typing import Dict, Set

# external
import tomlkit
from dephell_argparse import CommandHandler

# app
from ..actions import attach_deps, get_python_env
from ..cached_property import cached_property
from ..config import Config, config, get_data_dir
from ..constants import CONFIG_NAMES, ENV_VAR_TEMPLATE, GLOBAL_CONFIG_NAME
from ..controllers import analyze_conflict
from ..converters import CONVERTERS, InstalledConverter


REX_WORD = re.compile(r'([a-z\d])([A-Z])')


class BaseCommand(CommandHandler):
    logger = getLogger('dephell.commands')
    prog = 'dephell'
    find_config = True

    @cached_property
    def config(self) -> Config:
        config.setup_logging()
        self._attach_global_config_file()
        self._attach_config_file(path=self.args.config, env=self.args.env)
        config.attach_env_vars()
        config.attach_cli(self.args)
        config.setup_logging()
        return config

    def validate(self) -> bool:
        is_valid = self.config.validate()
        if not is_valid:
            self.logger.error('invalid config')
            print(self.config.format_errors())
        return is_valid

    # properties

    @cached_property
    def url(self) -> str:
        tmpl = 'https://dephell.org/docs/cmd-{}.html'
        return tmpl.format(self.name.replace(' ', '-'))

    @cached_property
    def usage(self) -> str:
        return 'dephell {} [OPTIONS]'.format(self.name)

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
        # get params from env vars if are not specified
        if path is None:
            path = environ.get(ENV_VAR_TEMPLATE.format('CONFIG'))
        if env is None:
            env = environ.get(ENV_VAR_TEMPLATE.format('ENV'), 'main')

        # if path to config specified explicitly, just use it
        if path:
            config.attach_file(path=path, env=env)
            return True

        # do not implicitly attach file for some commands like `jail`
        if not cls.find_config:
            cls.logger.debug('cannot find config file')
            return False

        # if path isn't specified, carefully try default names
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
            self.logger.error('cannot find dependency file', extra=dict(path=loader_config['path']))
            return None

        self.logger.info('get dependencies', extra=dict(
            format=loader_config['format'],
            path=loader_config['path'],
        ))
        loader = CONVERTERS[loader_config['format']]
        loader = loader.copy(project_path=Path(self.config['project']))
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
        if self.config.get('envs'):
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

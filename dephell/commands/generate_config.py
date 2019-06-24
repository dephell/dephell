# built-in
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path

# external
import tomlkit

# app
from ..config import builders, config
from ..constants import PAIRS, SUFFIXES
from ..converters import CONVERTERS
from .base import BaseCommand


class GenerateConfigCommand(BaseCommand):
    """Create config file for DepHell.

    https://dephell.readthedocs.io/cmd-generate-config.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell generate config',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    @classmethod
    def get_config(cls, args):
        config.setup_logging()
        config.attach_cli(args)
        config.setup_logging()
        if 'config' not in config._data:
            config._data['config'] = 'pyproject.toml'
        return config

    def validate(self):
        return True

    @staticmethod
    def _make_env(from_format, from_path, to_format, to_path):
        table = tomlkit.table()

        table['from'] = tomlkit.inline_table()
        table['from']['format'] = from_format
        table['from']['path'] = from_path

        table['to'] = tomlkit.inline_table()
        table['to']['format'] = to_format
        table['to']['path'] = to_path

        return table

    def __call__(self) -> bool:
        config_path = Path(self.config['config'])
        exists = config_path.exists()
        if exists:
            # read
            with config_path.open('r', encoding='utf8') as stream:
                doc = tomlkit.parse(stream.read())
        else:
            doc = tomlkit.document()

        # add section
        if 'tool' not in doc:
            doc.add('tool', tomlkit.table())
        if 'dephell' not in doc['tool']:
            doc['tool'].add('dephell', tomlkit.table())

        # detect requirements files
        project_path = Path(self.config['project'])
        parsable_files = defaultdict(list)
        for file_path in project_path.iterdir():
            if file_path.suffix not in SUFFIXES:
                continue
            content = None if file_path.is_dir() else file_path.read_text()
            for converter_name, converter in CONVERTERS.items():
                if converter.can_parse(path=file_path, content=content):
                    parsable_files[converter_name].append(file_path.name)
        for from_format, to_format in PAIRS:
            for from_path in parsable_files[from_format]:
                for to_path in parsable_files[to_format]:
                    if from_format not in doc['tool']['dephell']:
                        doc['tool']['dephell'].add(
                            from_format,
                            self._make_env(from_format, from_path, to_format, to_path),
                        )

        if not doc['tool']['dephell'].value:
            if 'example' not in doc['tool']['dephell']:
                doc['tool']['dephell'].add(
                    'example',
                    self._make_env('pip', 'requirements.in', 'piplock', 'requirements.lock'),
                )

        # write
        with config_path.open('w', encoding='utf8') as stream:
            stream.write(tomlkit.dumps(doc))

        if exists:
            self.logger.info('pyproject.toml updated')
        else:
            self.logger.info('pyproject.toml created')
        return True

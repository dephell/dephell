# built-in
from argparse import ArgumentParser

# external
from dephell_venvs import VEnvs
from packaging.utils import canonicalize_name

# app
from ..actions import format_size, get_entrypoints, get_path_size, make_json
from ..config import builders
from .base import BaseCommand


class JailShowCommand(BaseCommand):
    """Show info about the package isolated environment.
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', help='jail name')
        return parser

    def __call__(self) -> bool:
        venvs = VEnvs(path=self.config['venv'])
        name = canonicalize_name(self.args.name)
        venv = venvs.get_by_name(name)
        if not venv.exists():
            self.logger.error('jail does not exist', extra=dict(package=name))
            return False

        entrypoints = get_entrypoints(venv=venv, name=name)
        entrypoints_names = []
        for entrypoint in entrypoints:
            if entrypoint.group != 'console_scripts':
                continue
            if not (venv.bin_path / entrypoint.name).exists():
                continue
            entrypoints_names.append(entrypoint.name)

        data = dict(
            name=name,
            path=str(venv.path),
            entrypoints=entrypoints_names,
            size=dict(
                lib=format_size(get_path_size(venv.lib_path)),
                total=format_size(get_path_size(venv.path)),
            )
        )

        print(make_json(
            data=data,
            key=self.config.get('filter'),
            colors=not self.config['nocolors'],
            table=self.config['table'],
        ))
        return True

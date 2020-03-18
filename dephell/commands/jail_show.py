# built-in
from argparse import ArgumentParser
from pathlib import Path

# external
from dephell_venvs import VEnvs
from packaging.utils import canonicalize_name

# app
from ..actions import format_size, get_path_size, make_json
from ..config import builders
from ..converters import InstalledConverter
from .base import BaseCommand


class JailShowCommand(BaseCommand):
    """Show info about the package isolated environment.
    """
    find_config = False

    @staticmethod
    def build_parser(parser) -> ArgumentParser:
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

        # get list of exposed entrypoints
        entrypoints_names = []
        for entrypoint in venv.bin_path.iterdir():
            global_entrypoint = Path(self.config['bin']) / entrypoint.name
            if not global_entrypoint.exists():
                continue
            if not global_entrypoint.resolve().samefile(entrypoint):
                continue
            entrypoints_names.append(entrypoint.name)

        root = InstalledConverter().load(paths=[venv.lib_path], names={name})
        version = None
        for subdep in root.dependencies:
            if subdep.name != name:
                continue
            version = str(subdep.constraint).replace('=', '')

        data = dict(
            name=name,
            path=str(venv.path),
            entrypoints=entrypoints_names,
            version=version,
            size=dict(
                lib=format_size(get_path_size(venv.lib_path)),
                total=format_size(get_path_size(venv.path)),
            ),
        )

        print(make_json(
            data=data,
            key=self.config.get('filter'),
            colors=not self.config['nocolors'],
            table=self.config['table'],
        ))
        return True

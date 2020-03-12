# built-in
from argparse import ArgumentParser

# external
from dephell_shells import Shells

# app
from ..actions import format_size, get_path_size, get_venv, make_json
from ..config import builders
from .base import BaseCommand


class InspectVenvCommand(BaseCommand):
    """Show virtual environment information for current project.
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        venv = get_venv(config=self.config)
        shells = Shells(bin_path=venv.bin_path)

        data = dict(
            exists=venv.exists(),
            paths=dict(
                venv=str(venv.path),
                project=self.config['project'],
            ),
        )

        if venv.exists():
            data['paths'].update(dict(
                activate=str(venv.bin_path / shells.current.activate),
                bin=str(venv.bin_path),
                lib=str(venv.lib_path),
                python=str(venv.python_path),
            ))
            impl = venv.python.implementation
            if impl == 'python':
                impl = 'cpython'
            data.update(dict(
                sizes=dict(
                    lib=format_size(get_path_size(venv.lib_path)),
                    venv=format_size(get_path_size(venv.path)),
                ),
                python=dict(
                    version=str(venv.python.version),
                    implementation=impl,
                ),
            ))
        print(make_json(
            data=data,
            key=self.config.get('filter'),
            colors=not self.config['nocolors'],
            table=self.config['table'],
        ))
        return True

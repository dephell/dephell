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

    https://dephell.readthedocs.io/en/latest/cmd-inspect-venv.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell inspect venv',
            description=cls.__doc__,
        )
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
            venv=str(venv.path),
            project=self.config['project'],
        )

        if venv.exists():
            data.update(dict(
                activate=str(venv.bin_path / shells.current.activate),
                bin=str(venv.bin_path),
                lib=str(venv.lib_path),
                lib_size=format_size(get_path_size(venv.lib_path)),
                python=str(venv.python_path),
            ))
        print(make_json(data=data, key=self.config.get('filter')))
        return True

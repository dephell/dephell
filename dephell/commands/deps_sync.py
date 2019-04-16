# built-in
from argparse import ArgumentParser

# app
from ..config import builders
from .deps_install import DepsInstallCommand


class DepsSyncCommand(DepsInstallCommand):
    """Install project dependencies with removing all other packages from venv.

    https://dephell.readthedocs.io/en/latest/cmd-deps-sync.html
    """
    # DepsInstallCommand contains all logic for sync.
    # There we just set `sync` flag and change some minor metainfo.
    sync = True

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell deps sync',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_to(parser)
        builders.build_resolver(parser)
        builders.build_api(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

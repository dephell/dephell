# built-in
from argparse import ArgumentParser
from collections import defaultdict

# app
from ..actions import make_json
from ..config import builders
from .base import BaseCommand


class DepsLicensesCommand(BaseCommand):
    """Show licenses for all project dependencies.

    https://dephell.readthedocs.io/cmd-deps-licenses.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell deps licenses',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_resolver(parser)
        builders.build_api(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        resolver = self._get_locked()
        if resolver is None:
            return False

        # get licenses
        licenses = defaultdict(set)
        for dep in resolver.graph:
            if dep.license:
                license = dep.license if isinstance(dep.license, str) else dep.license.id
                licenses[license].add(dep.name)
            else:
                licenses['Unknown'].add(dep.name)
        licenses = {name: sorted(deps) for name, deps in licenses.items()}
        print(make_json(data=licenses, key=self.config.get('filter'), sep=None))
        return True

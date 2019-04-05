# built-in
from argparse import ArgumentParser

# app
from ..actions import get_venv, make_json
from ..config import builders
from ..converters import InstalledConverter
from ..repositories import WareHouseRepo
from .base import BaseCommand


class PackageListCommand(BaseCommand):
    """Show all installed packages.

    https://dephell.readthedocs.io/en/latest/cmd-package-list.html
    """

    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell package list',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        return parser

    def __call__(self):
        venv = get_venv(config=self.config)
        if venv.exists():
            path = venv.lib_path
        else:
            path = None
            self.logger.warning('venv not found, package version will be shown for global python lib')

        converter = InstalledConverter()
        root = converter.load(path=path)

        repo = WareHouseRepo()
        data = []
        for dep in root.dependencies:
            releases = repo.get_releases(dep)
            data.append(dict(
                name=dep.name,
                latest=str(releases[0].version),
                installed=str(dep.constraint).replace('=', '').split(' || '),
                description=dep.description,

                license=getattr(dep.license, 'id', dep.license),
                links=dep.links,
                authors=[str(author) for author in dep.authors],
            ))
        print(make_json(data=data, key=self.config.get('filter')))
        return True

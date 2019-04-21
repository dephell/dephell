# built-in
from argparse import ArgumentParser

# app
from ..actions import format_size, get_package, get_path_size, get_python_env, make_json
from ..config import builders
from ..converters import InstalledConverter
from .base import BaseCommand


class PackageShowCommand(BaseCommand):
    """Show information about package from PyPI.org.

    https://dephell.readthedocs.io/en/latest/cmd-package-show.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell package show',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', help='package name (and version)')
        return parser

    def __call__(self) -> bool:
        dep = get_package(self.args.name)
        releases = dep.repo.get_releases(dep)

        python = get_python_env(config=self.config)
        self.logger.debug('choosen python', extra=dict(path=str(python.path)))

        root = InstalledConverter().load(paths=python.lib_paths, names={self.args.name})
        local_versions = []
        local_places = []
        for subdep in root.dependencies:
            if subdep.name == dep.name:
                local_versions = str(subdep.constraint).replace('=', '').split(' || ')
                local_places.extend(subdep.locations)

        data = dict(
            name=dep.name,
            description=dep.description,
            latest=str(releases[0].version),
            license=getattr(dep.license, 'id', dep.license),
            links=dep.links,
            updated=str(releases[0].time.date()),
            authors=[str(author) for author in dep.authors],
        )

        if local_versions:
            data.update(dict(
                installed=local_versions,
                locations=sorted(map(str, local_places)),
                size=format_size(sum(get_path_size(place) for place in local_places)),
            ))

        print(make_json(data=data, key=self.config.get('filter')))
        return True

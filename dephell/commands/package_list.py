# built-in
from argparse import ArgumentParser

# app
from ..actions import get_python_env, make_json
from ..config import builders
from ..converters import InstalledConverter
from ..exceptions import PackageNotFoundError
from .base import BaseCommand


class PackageListCommand(BaseCommand):
    """Show all installed packages.

    https://dephell.readthedocs.io/cmd-package-list.html
    """

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell package list',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        python = get_python_env(config=self.config)
        self.logger.debug('choosen python', extra=dict(path=str(python.path)))
        root = InstalledConverter().load(paths=python.lib_paths)

        data = []
        for dep in root.dependencies:
            try:
                releases = dep.repo.get_releases(dep)
            except PackageNotFoundError as exc:
                self.logger.warning(str(exc), extra=exc.extra)
                continue

            data.append(dict(
                name=dep.name,
                latest=str(releases[0].version),
                installed=str(dep.constraint).replace('=', '').split(' || '),
                description=dep.description,

                license=getattr(dep.license, 'id', dep.license),
                links=dep.links,
                authors=[str(author) for author in dep.authors],
                updated=str(releases[0].time.date()),
            ))
        print(make_json(data=data, key=self.config.get('filter')))
        return True

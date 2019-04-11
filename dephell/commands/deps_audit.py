# built-in
from argparse import ArgumentParser

# app
from ..actions import get_packages, get_python_env, make_json
from ..config import builders
from ..controllers import Safety, Snyk
from ..converters import CONVERTERS, InstalledConverter
from .base import BaseCommand


class DepsAuditCommand(BaseCommand):
    """Show known vulnerabilities for project dependencies.

    https://dephell.readthedocs.io/en/latest/cmd-deps-audit.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell deps audit',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_to(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs='*', help='package name and version')
        return parser

    def __call__(self) -> bool:
        packages = None

        # get packages from CLI
        if self.args.name:
            packages = get_packages(reqs=self.args.name)
            for dep in packages:
                if not str(dep.constraint).startswith('=='):
                    self.logger.error('please, specify version for package', extra=dict(
                        package=dep.name,
                        constraint=str(dep.constraint),
                    ))
                    return False

        # get packages from lockfile
        if packages is None:
            loader_config = self.config.get('to') or self.config.get('from')
            if loader_config is not None:
                loader = CONVERTERS[loader_config['format']]
                if loader.lock:
                    self.logger.info('get dependencies from lockfile', extra=dict(
                        format=loader_config['format'],
                        path=loader_config['path'],
                    ))
                    root = loader.load(path=loader_config['path'])
                    packages = root.dependencies

        # get installed packages
        if packages is None:
            # get executable
            python = get_python_env(config=self.config)
            self.logger.debug('choosen python', extra=dict(path=str(python.path)))
            root = InstalledConverter().load(paths=python.lib_paths)
            packages = root.dependencies

        safety = Safety()
        snyk = Snyk()

        data = []
        for dep in packages:
            versions = str(dep.constraint).replace('=', '').split(' || ')
            for version in versions:
                vulns = safety.get(name=dep.name, version=version)
                vulns += snyk.get(name=dep.name, version=version)
                if not vulns:
                    continue
                releases = dep.repo.get_releases(dep)
                for vuln in vulns:
                    data.append(dict(
                        # local info
                        name=dep.name,
                        current=version,
                        # pypi info
                        latest=str(releases[0].version),
                        updated=str(releases[0].time.date()),
                        # vuln info
                        description=vuln.description,
                        links=vuln.links,
                        vulnerable=str(vuln.specifier),
                    ))

        if data:
            print(make_json(data=data, key=self.config.get('filter')))
            return False

        self.logger.info('dependencies has no known vulnerabilities (yet)')
        return True

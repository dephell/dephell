# built-in
from argparse import ArgumentParser

# app
from ..actions import attach_deps, get_python_env, make_json
from ..config import builders
from ..controllers import analyze_conflict
from ..converters import CONVERTERS, InstalledConverter
from ..models import Requirement
from .base import BaseCommand


class DepsCheckCommand(BaseCommand):
    """Show difference between venv and project dependencies.

    https://dephell.readthedocs.io/en/latest/cmd-deps-check.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell deps check',
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

    def __call__(self) -> bool:
        loader_config = self.config.get('to') or self.config['from']
        self.logger.info('get dependencies', extra=dict(
            format=loader_config['format'],
            path=loader_config['path'],
        ))
        loader = CONVERTERS[loader_config['format']]
        resolver = loader.load_resolver(path=loader_config['path'])
        attach_deps(resolver=resolver, config=self.config, merge=False)

        # resolve
        self.logger.info('build dependencies graph...')
        resolved = resolver.resolve(silent=self.config['silent'])
        if not resolved:
            conflict = analyze_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # get executable
        python = get_python_env(config=self.config)
        self.logger.debug('choosen python', extra=dict(path=str(python.path)))

        # get installed packages
        installed_root = InstalledConverter().load(paths=python.lib_paths)
        installed = {dep.name: str(dep.constraint).strip('=') for dep in installed_root.dependencies}

        # filter deps by envs and markers
        resolver.apply_envs(set(self.config.get('envs', {'main'})))
        resolver.apply_markers(python=python)

        data = []
        reqs = Requirement.from_graph(graph=resolver.graph, lock=True)
        for req in reqs:
            version = req.version.strip('=')
            # not installed
            if req.name not in installed:
                data.append(dict(
                    action='install',
                    name=req.name,
                    installed=None,
                    locked=version,
                ))
                continue
            # installed the same version, skip
            if version == installed[req.name]:
                continue
            # installed old version
            data.append(dict(
                action='update',
                name=req.name,
                installed=installed[req.name],
                locked=version,
            ))
        # obsolete
        names = set(installed) - {req.name for req in reqs}
        for name in names:
            data.append(dict(
                action='remove',
                name=name,
                installed=installed[name],
                locked=None,
            ))

        if data:
            print(make_json(data=data, key=self.config.get('filter')))
            return False

        self.logger.info('all packages is up-to-date')
        return True

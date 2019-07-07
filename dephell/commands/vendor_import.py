# built-in
from argparse import ArgumentParser
from pathlib import Path

from bowler import Query

# app
from ..actions import transform_imports
from ..config import builders
from .base import BaseCommand


class VendorImportCommand(BaseCommand):
    """Patch all imports in project to use vendored dependencies.

    https://dephell.readthedocs.io/en/latest/cmd-vendor-import.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell project vendorize',
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
        output_path = Path(self.config['vendor']['path'])
        self.logger.info('patching imports...')
        modules = self._patch_imports(resolver=resolver, output_path=output_path)
        self.logger.info('done!', extra=dict(modules=modules))
        return True

    def _patch_imports(self, resolver, output_path: Path) -> int:
        # select modules to patch imports
        query = Query()
        query.paths = []
        for package in resolver.graph.metainfo.package.packages:
            for module_path in package:
                query.paths.append(str(module_path))

        # patch vendors if it's outside of main package
        package_path = resolver.graph.metainfo.package.packages[0].path
        if package_path.resolve() not in output_path.resolve().parents:
            query.paths.append(str(output_path))

        # set renamings
        root = Path(self.config['project'])
        for library in output_path.iterdir():
            if library.name in self.config['vendor']['exclude']:
                continue
            library_module = '.'.join(library.resolve().relative_to(str(root)).parts)
            self.logger.debug('patch imports', extra=dict(
                old_name=library.name,
                new_name=library_module,
            ))
            query = transform_imports(
                query=query,
                old_name=library.name,
                new_name=library_module,
            )

        # execute renaming
        query.execute(interactive=False, write=True, silent=True)
        return len(query.paths)

# built-in
import asyncio
import shutil
from argparse import ArgumentParser
from tempfile import TemporaryDirectory
from pathlib import Path

from bowler import Query
from packaging.utils import canonicalize_name

# app
from ..config import builders
from .base import BaseCommand


class ProjectVendorizeCommand(BaseCommand):
    """Vendorize project dependencies.

    https://dephell.readthedocs.io/en/latest/cmd-project-vendorize.html
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
        parser.add_argument('--vendors', help='path to vendorized packages')
        return parser

    def __call__(self) -> bool:
        resolver = self._get_locked()
        if resolver is None:
            return False
        output_path = Path(self.config['vendors'])

        self.logger.info('downloding packages...', extra=dict(output=output_path))
        packages = self._download_packages(resolver=resolver, output_path=output_path)

        self.logger.info('patching imports...')
        modules = self._patch_imports(resolver=resolver, output_path=output_path)

        self.logger.info('done!', extra=dict(packages=packages, modules=modules))
        return True

    def _download_packages(self, resolver, output_path: Path) -> int:
        with TemporaryDirectory() as archives_path:
            archives_path = Path(archives_path)

            loop = asyncio.get_event_loop()
            tasks = []
            for dep in resolver.graph:
                tasks.append(dep.repo.download(
                    name=dep.name,
                    version=dep.group.best_release.version,
                    path=archives_path,
                ))
            loop.run_until_complete(asyncio.gather(*tasks))

            # say to shutils that wheel can be parsed as zip
            shutil.register_unpack_format(
                name='wheel',
                extensions=['.whl'],
                function=shutil._unpack_zipfile,
            )

            for archive_path in archives_path.iterdir():
                self._extract_modules(
                    dep=dep,
                    archive_path=archive_path,
                    output_path=output_path,
                )
        return len(tasks)

    def _extract_modules(self, dep, archive_path, output_path: Path) -> None:
        with TemporaryDirectory() as package_path:
            package_path = Path(package_path)
            shutil.unpack_archive(str(archive_path), str(package_path))
            if len(list(package_path.iterdir())) == 1:
                package_path = next(package_path.iterdir())

            for module_path in package_path.iterdir():
                if canonicalize_name(module_path.name) not in (dep.name, dep.name + '-py'):
                    continue
                self.info('copying module', extra=dict(
                    path=module_path.name,
                    dependency=dep.name,
                    version=dep.group.best_release.version,
                ))
                shutil.copytree(str(module_path), str(output_path / module_path.name))

    def _patch_imports(self, resolver, output_path) -> int:
        # select modules to patch imports
        query = Query()
        query.paths = []
        for package in resolver.graph.metainfo.package.packages:
            for module_path in package:
                query.paths.append(str(module_path))

        # set renamings
        root = Path(self.config['project'])
        for library in output_path.iterdir():
            library_module = '.'.join(library.relative_to(root).parts)
            query = query.select_module(library.name).rename(library_module)

        # execute renaming
        query.execute(interactive=False, write=True, silent=True)
        return len(query.paths)

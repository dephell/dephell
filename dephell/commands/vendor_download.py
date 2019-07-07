# built-in
import asyncio
import shutil
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

from dephell_discover import Root as PackageRoot

# app
from ..config import builders
from .base import BaseCommand


class VendorDownloadCommand(BaseCommand):
    """Download and extract project dependencies.

    https://dephell.readthedocs.io/en/latest/cmd-vendor-download.html
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
        self.logger.info('downloading packages...', extra=dict(output=output_path))
        packages = self._download_packages(
            resolver=resolver,
            output_path=output_path,
            exclude=self.config['vendor']['exclude'],
        )
        (output_path / '__init__.py').touch(0o777)
        self.logger.info('done!', extra=dict(packages=packages))
        return True

    def _download_packages(self, resolver, output_path: Path,
                           exclude: Iterable[str] = None) -> int:
        exclude = set(exclude or [])
        with TemporaryDirectory() as archives_path:
            archives_path = Path(archives_path)

            loop = asyncio.get_event_loop()
            tasks = []
            deps = []
            for dep in resolver.graph:
                if dep.name in exclude:
                    self.logger.debug('exclude package', extra=dict(package_name=dep.name))
                    continue

                deps.append(dep)
                tasks.append(dep.repo.download(
                    name=dep.name,
                    version=dep.group.best_release.version,
                    path=archives_path,
                ))
            loop.run_until_complete(asyncio.gather(*tasks))

            for dep, archive_path in zip(deps, archives_path.iterdir()):
                self._extract_modules(
                    dep=dep,
                    archive_path=archive_path,
                    output_path=output_path,
                )
        return len(tasks)

    def _extract_modules(self, dep, archive_path: Path, output_path: Path) -> bool:
        # say to shutils that wheel can be parsed as zip
        if 'wheel' not in shutil._UNPACK_FORMATS:
            shutil.register_unpack_format(
                name='wheel',
                extensions=['.whl'],
                function=shutil._unpack_zipfile,
            )

        with TemporaryDirectory(suffix=dep.name) as package_path:
            package_path = Path(package_path)
            shutil.unpack_archive(str(archive_path), str(package_path))
            if len(list(package_path.iterdir())) == 1:
                package_path = next(package_path.iterdir())

            # find modules
            root = PackageRoot(name=dep.name, path=package_path)
            if not root.packages:
                self.logger.error('cannot find modules', extra=dict(
                    dependency=dep.name,
                    version=dep.group.best_release.version,
                ))
                return False

            # copy modules
            module_path = root.packages[0].path
            module_name = root.packages[0].module
            self.logger.info('copying module...', extra=dict(
                path=str(module_path.relative_to(package_path)),
                dependency=dep.name,
            ))
            shutil.copytree(
                src=str(module_path),
                dst=str(output_path.joinpath(*module_name.split('.'))),
            )
            return True

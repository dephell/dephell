# built-in
from io import BytesIO
from itertools import chain
from pathlib import Path
from tarfile import TarFile, TarInfo
from tempfile import TemporaryDirectory
from typing import Optional

# external
import attr
from dephell_archive import ArchivePath

# app
from ..config import config
from ..controllers import Readme
from ..models import RootDependency
from .base import BaseConverter
from .egginfo import EggInfoConverter


@attr.s()
class SDistConverter(BaseConverter):
    # place all files into subdir
    subdir = attr.ib(type=bool, default=True)
    # ratio of tests and project size after which tests will be excluded from sdist
    ratio = attr.ib(type=Optional[float], default=None)

    lock = False

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if content is not None:
            return False
        if path.name == 'dist':
            return True
        return (path.suffix in ('.zip', '.gz', '.tar'))

    def load(self, path) -> RootDependency:
        path = Path(str(path))
        if path.suffix not in ('.zip', '.gz', '.tar', '.tgz', '.bz2'):
            raise ValueError('invalid file extension: ' + path.suffix)
        root = None
        converter = EggInfoConverter()
        with TemporaryDirectory() as cache:
            archive = ArchivePath(archive_path=path, cache_path=Path(cache))

            # read *.egg-info
            paths = chain(
                archive.glob('*.egg-info'),
                archive.glob('*/*.egg-info'),
                archive.glob('src/*.egg-info'),
                archive.glob('src/*/*.egg-info'),
            )
            paths = [path for path in paths if 'tests' not in path.parts]
            if paths:
                root = converter.load_dir(*paths)
                root.readme = Readme.discover(path=archive)
                return root

            # read metainfo from PKG-INFO
            paths = archive.glob('**/PKG-INFO')
            paths = [path for path in paths if 'tests' not in path.parts]
            if paths:
                with paths[0].open('r') as stream:
                    root = converter.parse_info(content=stream.read())

            # read dependencies from requires.txt
            if root is None or not root.dependencies:
                paths = list(archive.glob('**/requires.txt'))
                paths = [path for path in paths if 'tests' not in path.parts]
                if paths:
                    with paths[0].open('r') as stream:
                        root = converter.parse_requires(content=stream.read(), root=root)

        if root is None:
            msg = 'cannot find any metainfo in the archive: '
            raise FileNotFoundError(msg + str(archive.archive_path))
        return root

    def dump(self, reqs, path: Path, project: RootDependency) -> None:
        project_name = project.raw_name.replace('-', '_')
        release_name = '{name}-{version}'.format(
            name=project.raw_name,
            version=project.pep_version,
        )
        subdir = release_name + '/' if self.subdir else ''

        if isinstance(path, str):
            path = Path(path)
        if not path.name.endswith('.tar.gz'):
            path /= release_name + '.tar.gz'
        path.parent.mkdir(exist_ok=True, parents=True)
        if path.exists():
            path.unlink()

        converter = EggInfoConverter()
        info = converter.make_info(reqs=reqs, project=project, with_requires=False)
        getters = {
            'dependency_links.txt': lambda: converter.make_dependency_links(reqs=reqs),
            'entry_points.txt': lambda: converter.make_entrypoints(project=project),
            'PKG-INFO': lambda: info,
            'requires.txt': lambda: converter.make_requires(reqs=reqs),
            'SOURCES.txt': lambda: converter.make_sources(project=project),
            'top_level.txt': lambda: converter.make_top_level(project=project),
        }

        with TarFile.open(str(path), mode='w:gz') as tar:

            # write metafiles
            self._write_content(tar=tar, path=subdir + 'PKG-INFO', content=info)
            for file_name, getter in getters.items():
                fpath = '{subdir}{project}.egg-info/{file}'.format(
                    subdir=subdir,
                    project=project_name,
                    file=file_name,
                )
                self._write_content(tar=tar, path=fpath, content=getter())

            # write packages
            for package in chain(project.package.packages, project.package.data):
                for full_path in package:
                    fpath = '{subdir}{module}'.format(
                        subdir=subdir,
                        module='/'.join(full_path.relative_to(project.package.path).parts),
                    )
                    tar.add(name=str(full_path), arcname=fpath, filter=self._set_uid_gid)

            self._write_additional_files(tar=tar, project=project, subdir=subdir)

    def _write_additional_files(self, *, tar, project, subdir):
        # write readme
        if project.readme:
            tar.add(
                name=str(project.readme.path),
                arcname=subdir + project.readme.path.name,
                filter=self._set_uid_gid,
            )
            if project.readme.markup != 'rst':
                rst = project.readme.to_rst()
                tar.add(
                    name=str(rst.path),
                    arcname=subdir + rst.path.name,
                    filter=self._set_uid_gid,
                )
            elif (project.package.path / 'README.md').exists():
                tar.add(
                    name=str(project.package.path / 'README.md'),
                    arcname=subdir + 'README.md',
                    filter=self._set_uid_gid,
                )

        # write setup files
        path = project.package.path
        for fname in ('setup.cfg', 'setup.py'):
            if (path / fname).exists():
                tar.add(
                    name=str(path / fname),
                    arcname=subdir + fname,
                    filter=self._set_uid_gid,
                )

        # write license files
        patterns = ('LICEN[CS]E*', 'COPYING*', 'NOTICE*', 'AUTHORS*')
        for pattern in patterns:
            for file_path in project.package.path.glob(pattern):
                if not file_path.is_file():
                    continue
                tar.add(
                    name=str(file_path),
                    arcname=subdir + file_path.name,
                    filter=self._set_uid_gid,
                )

        # write tests
        from ..actions import get_path_size
        if self.ratio is None:
            self.ratio = config['sdist']['ratio']
        tests_path = Path('tests')
        if tests_path.exists():
            package_size = get_path_size(path=project.package.packages[0].path)
            tests_size = get_path_size(path=tests_path)
            if package_size * self.ratio > tests_size:
                tar.add(
                    name=str(tests_path),
                    arcname=subdir + tests_path.name,
                    filter=self._set_uid_gid,
                )

    def _write_content(self, tar, path: str, content) -> None:
        content = content.encode('utf-8')
        tar_info = TarInfo(path)
        tar_info.size = len(content)
        tar_info = self._set_uid_gid(tar_info)
        tar.addfile(tar_info, BytesIO(content))

    # poetry/masonry/builders/sdist.py:clean_tarinfo
    @staticmethod
    def _set_uid_gid(tarinfo: TarInfo) -> TarInfo:
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = ''

        # Set 644 permissions, leaving higher bits of st_mode unchanged
        new_mode = (tarinfo.mode | 0o644) & ~0o133
        if tarinfo.mode & 0o100:
            new_mode |= 0o111  # Executable: 644 -> 755
        tarinfo.mode = new_mode

        return tarinfo

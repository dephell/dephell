# built-in
import subprocess
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

# external
from dephell_pythons import Python

# app
from ..actions import attach_deps, get_python
from ..config import builders
from ..controllers import analyze_conflict
from ..converters import CONVERTERS
from ..models import Requirement
from .base import BaseCommand


# https://docs.python.org/3/library/site.html
PTHS = ('easy-install.pth', 'setuptools.pth', None)
DIRS = ('site-packages', 'dist-packages')


class ProjectRegisterCommand(BaseCommand):
    """Register the project in the system.
    """
    @staticmethod
    def build_parser(parser) -> ArgumentParser:
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        # read deps file
        if 'from' not in self.config:
            self.logger.error('`--from` is required for this command')
            return False
        loader = CONVERTERS[self.config['from']['format']]
        loader = loader.copy(project_path=Path(self.config['project']))
        resolver = loader.load_resolver(path=self.config['from']['path'])
        if loader.lock:
            self.logger.warning('do not build project from lockfile!')

        # attach
        merged = attach_deps(resolver=resolver, config=self.config, merge=True)
        if not merged:
            conflict = analyze_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # create egg-info
        project_path = Path(self.config['project'])
        reqs = Requirement.from_graph(resolver.graph, lock=False)
        self.logger.info('creating egg-info...')
        dumper = CONVERTERS['egginfo']
        dumper = dumper.copy(project_path=Path(self.config['project']))
        dumper.dump(
            path=project_path,
            reqs=reqs,
            project=resolver.graph.metainfo,
        )

        self.logger.info('creating egg-link...')
        python = get_python(self.config)
        self.logger.debug('python found', extra=dict(python=str(python.path)))
        lib_path = self._get_lib_path(python=python)
        if lib_path is None:
            self.logger.error('cannot find site-packages path', extra=dict(python=str(python.path)))
            return False
        self.logger.debug('lib found', extra=dict(python=str(lib_path)))
        ok = self._upd_egg_link(lib_path=lib_path, project_path=project_path)
        if not ok:
            return False
        self._upd_pth(lib_path=lib_path, project_path=project_path)
        self.logger.info('registered!', extra=dict(python=str(python.path.name)))
        return True

    @staticmethod
    def _get_lib_path(python: Python) -> Optional[Path]:
        """Find site-packages or dist-packages dir for the given python
        """
        cmd = [str(python.path), '-c', r'print(*__import__("sys").path, sep="\n")']
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        if result.returncode != 0:
            return None
        paths = []
        for path in result.stdout.decode().splitlines():
            path = Path(path)
            if not path.exists():
                continue
            paths.append(path)

        for pth in PTHS:
            for dir_name in DIRS:
                for path in paths:
                    if path.name != dir_name:
                        continue
                    if pth and not (path / pth).exists():
                        continue
                    return path
        return None

    def _upd_egg_link(self, lib_path: Path, project_path: Path) -> bool:
        # find the correct one egg-info
        info_path = (project_path / project_path.name).with_suffix('.egg-info')
        if not info_path.exists():
            paths = list(project_path.glob('*.egg-info'))
            if len(paths) != 1:
                self.logger.warning('cannot find egg-info')
                return False
            info_path = paths[0]
        self.logger.debug('egg-info found', extra=dict(path=str(info_path)))

        # create egg-link
        link_path = (lib_path / info_path.name).with_suffix('.egg-link')
        link_path.write_text(str(info_path) + '\n.')
        self.logger.debug('egg-link created', extra=dict(path=str(link_path)))
        return True

    def _upd_pth(self, lib_path: Path, project_path: Path):
        # read existing content
        pth_path = lib_path / 'dephell.pth'
        content = ''
        if pth_path.exists():
            content = pth_path.read_text()

        # check if already added
        paths = content.splitlines()
        if str(project_path) in paths:
            self.logger.debug('already registered in pth', extra=dict(path=str(pth_path)))
            return

        # add
        content = content.rstrip() + '\n' + str(project_path) + '\n'
        pth_path.write_text(content.lstrip())
        self.logger.debug('pth updated', extra=dict(path=str(pth_path)))

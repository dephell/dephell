# built-in
from argparse import ArgumentParser
from pathlib import Path

# app
from ..actions import get_lib_path, get_python
from ..config import builders
from ..converters import CONVERTERS
from ..models import Requirement
from .base import BaseCommand


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
        # make egg-info
        if 'from' not in self.config:
            self.logger.error('`--from` is required for this command')
            return False
        project_path = Path(self.config['project'])
        ok = self._make_egg_info(
            project_path=project_path,
            from_format=self.config['from']['format'],
            from_path=self.config['from']['path'],
        )
        if not ok:
            return False

        # make egg-link
        self.logger.info('creating egg-link...')
        python = get_python(self.config)
        self.logger.debug('python found', extra=dict(python=str(python.path)))
        lib_path = get_lib_path(python_path=python.path)
        if lib_path is None:
            self.logger.error('cannot find site-packages path', extra=dict(python=str(python.path)))
            return False
        self.logger.debug('lib found', extra=dict(python=str(lib_path)))
        ok = self._upd_egg_link(lib_path=lib_path, project_path=project_path)
        if not ok:
            return False

        # update pth
        self._upd_pth(lib_path=lib_path, project_path=project_path)
        self.logger.info('registered!', extra=dict(python=str(python.path.name)))
        return True

    def _make_egg_info(self, project_path: Path, from_format: str, from_path: str) -> bool:
        loader = CONVERTERS[from_format]
        loader = loader.copy(project_path=project_path)
        resolver = loader.load_resolver(path=from_path)
        if loader.lock:
            self.logger.warning('do not build project from lockfile!')

        # We don't attach deps here.
        # Use `deps convert` before to merge deps if you need it.
        # Please, open an issue if it is a case for you.

        # create egg-info
        reqs = Requirement.from_graph(resolver.graph, lock=False)
        self.logger.info('creating egg-info...')
        dumper = CONVERTERS['egginfo']
        dumper = dumper.copy(project_path=project_path)
        dumper.dump(
            path=project_path,
            reqs=reqs,
            project=resolver.graph.metainfo,
        )

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

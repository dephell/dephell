# built-in
import shutil
from argparse import ArgumentParser
from pathlib import Path

# app
from ..config import builders
from ..controllers import analize_conflict
from ..converters import EggInfoConverter, PIPConverter
from ..models import Requirement
from ..package_manager import PackageManager
from ..utils import is_windows
from ..venvs import VEnvs
from .create import CreateCommand


class GetCommand(CreateCommand):
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='python3 -m dephell get',
            description='download and install package into isolated environment',
        )
        builders.build_config(parser)
        builders.build_venv(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        parser.add_argument('name', nargs='?')
        return parser

    def __call__(self) -> bool:
        resolver = PIPConverter(lock=False).loads_resolver(self.args.name)
        name = next(iter(resolver.graph.get_layer(0))).dependencies[0].name

        # resolve (and merge)
        self.logger.info('build dependencies graph...')
        resolved = resolver.resolve()
        if not resolved:
            conflict = analize_conflict(resolver=resolver)
            self.logger.warning('conflict was found')
            print(conflict)
            return False

        # get executable
        venvs = VEnvs(path=self.config['venv'], env=self.config.env)
        venv = venvs.get(Path(name), is_project=False)
        if venv.exists():
            self.logger.warning('remove installed version', extra=dict(package=name))
            shutil.rmtree(venv.path)
        python = self._get_python()
        self.logger.info('creating venv...', extra=dict(path=venv.path))
        venv.create(python_path=python.path)

        # install
        reqs = Requirement.from_graph(graph=resolver.graph, lock=True)
        self.logger.info('installation...', extra=dict(
            executable=venv.python_path,
            packages=len(reqs),
        ))
        PackageManager(executable=venv.python_path).install(reqs=reqs)

        # get entrypoints
        if not venv.lib_path:
            self.logger.critical('cannot locate lib path in the venv')
            return False
        paths = list(venv.lib_path.glob('{}*.*-info'.format(name)))
        if not paths:
            self.logger.critical('cannot locate dist-info for installed package')
            return False
        path = paths[0] / 'entry_points.txt'
        if not path.exists():
            self.logger.error('cannot find any entrypoints for package')
            return False
        entrypoints = EggInfoConverter().parse_entrypoints(content=path.read_text()).entrypoints

        # copy console scripts
        self.logger.info('copy executables...', extra=dict(package=name, path=self.config['bin']))
        for entrypoint in entrypoints:
            if entrypoint.group != 'console_scripts':
                continue
            if not (venv.bin_path / entrypoint.name).exists():
                self.logger.error('cannot find script in venv', extra=dict(script=entrypoint.name))
            else:
                self._publish_script(
                    src=venv.bin_path / entrypoint.name,
                    dst=Path(self.config['bin']) / entrypoint.name,
                )
                self.logger.info('copied', extra=dict(script=entrypoint.name))

        return True

    @staticmethod
    def _publish_script(src: Path, dst: Path):
        if dst.exists():
            dst.unlink()
        if is_windows():
            shutil.copy(str(src), str(dst))
        else:
            dst = dst.resolve()
            dst.symlink_to(src)

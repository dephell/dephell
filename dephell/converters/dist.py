from pathlib import Path

import pkginfo
from packaging.requirements import Requirement

from .base import BaseConverter
from ..models import Dependency, RootDependency


class DistConverter(BaseConverter):

    def load(self, path) -> RootDependency:
        path = Path(str(path))
        parser = self._get_parser(path)
        info = parser(str(path))

        deps = []
        root = RootDependency(name=self._get_name(path=path))
        for req in info.requires_dist:
            req = Requirement(req)
            deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

    @staticmethod
    def _get_parser(path):
        if not path.exists():
            raise FileNotFoundError

        if path.isdir():
            if (path / 'PKG-INFO').exists():
                return pkginfo.UnpackedSDist
            return pkginfo.Develop

        if path.name in ('PKG-INFO', 'setup.py'):
            return pkginfo.UnpackedSDist

        ext = str(path).rsplit('.', maxsplit=1)[-1]
        if ext == 'whl':
            return pkginfo.Wheel
        if ext in ('zip', 'gz', 'bz2'):
            return pkginfo.SDist
        if ext == 'egg':
            return pkginfo.BDist

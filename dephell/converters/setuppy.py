from distutils.core import run_setup
from packaging.requirements import Requirement

# app
from ..models import Dependency, RootDependency
from .base import BaseConverter


class SetupPyConverter(BaseConverter):
    lock = False

    def load(self, path) -> RootDependency:
        deps = []
        root = RootDependency(name=self._get_name(path=path))
        info = run_setup(str(path))
        for req in info.install_requires:
            req = Requirement(req)
            deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, content=None) -> str:
        raise NotImplementedError('dumping to setup.py is not supported yet')

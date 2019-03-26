# built-in
import sys
from pathlib import Path

# app
from .base import BaseConverter
from .egginfo import EggInfoConverter
from .wheel import WheelConverter
from ..models import RootDependency
from ..controllers import DependencyMaker


class InstalledConverter(BaseConverter):
    lock = True

    def load(self, path=None) -> RootDependency:
        paths = [path] if path else sys.path
        root = RootDependency(raw_name='installed')
        deps = []
        for path in paths:
            if isinstance(path, str):
                path = Path(path)
            for info_path in path.glob('*.egg-info'):
                subroot = EggInfoConverter().load(info_path)
                dep = DependencyMaker.from_root(dep=subroot, root=root)
                deps.append(dep)
            for info_path in path.glob('*.dist-info'):
                subroot = WheelConverter().load(info_path)
                dep = DependencyMaker.from_root(dep=subroot, root=root)
                deps.append(dep)
        root.attach_dependencies(deps)
        return root

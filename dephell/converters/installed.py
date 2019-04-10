# built-in
import sys
from pathlib import Path

# app
from ..controllers import DependencyMaker
from ..models import RootDependency
from .base import BaseConverter
from .egginfo import EggInfoConverter
from .wheel import WheelConverter


class InstalledConverter(BaseConverter):
    lock = True

    def load(self, path=None, paths=None) -> RootDependency:
        if paths is None:
            if path is not None:
                paths = [path]
            else:
                paths = sys.path

        root = RootDependency(raw_name='installed')
        parsers = [
            (EggInfoConverter(), '*.egg-info'),
            (WheelConverter(), '*.dist-info'),
        ]
        all_deps = dict()
        for path in paths:
            if isinstance(path, str):
                path = Path(path)
            for converter, pattern in parsers:
                for info_path in path.glob(pattern):
                    subroot = converter.load(info_path)
                    deps = DependencyMaker.from_root(dep=subroot, root=root)
                    for dep in deps:
                        if dep.name in all_deps:
                            all_deps[dep.name] |= dep
                        else:
                            all_deps[dep.name] = dep
        root.attach_dependencies(all_deps.values())
        return root

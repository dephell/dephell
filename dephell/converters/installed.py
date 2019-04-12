# built-in
import sys
from pathlib import Path
from typing import Union, Iterable

from packaging.utils import canonicalize_name

# app
from ..controllers import DependencyMaker
from ..models import RootDependency
from .base import BaseConverter
from .egginfo import EggInfoConverter
from .wheel import WheelConverter


class InstalledConverter(BaseConverter):
    lock = True

    # https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1635463
    _blacklist = {'pkg-resources'}

    def load(self, path: Union[Path, str] = None, paths: Iterable[Union[Path, str]] = None,
             names: Iterable[str] = None) -> RootDependency:
        if names:
            names = {canonicalize_name(name).replace('-', '_') for name in names}

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
                    name = info_path.with_suffix('').name.split('-')[0]
                    if names is not None and name not in names:
                        continue
                    subroot = converter.load_dir(info_path)
                    deps = DependencyMaker.from_root(dep=subroot, root=root)
                    for dep in deps:
                        if dep.name in self._blacklist:
                            continue
                        if dep.name in all_deps:
                            all_deps[dep.name] |= dep
                        else:
                            all_deps[dep.name] = dep
        root.attach_dependencies(all_deps.values())
        return root

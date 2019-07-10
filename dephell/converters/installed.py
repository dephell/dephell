# built-in
import sys
from pathlib import Path
from typing import Iterable, Union

# external
from dephell_discover import Root as PackageRoot
from packaging.utils import canonicalize_name

# app
from ..controllers import DependencyMaker
from ..models import RootDependency
from .base import BaseConverter
from .egginfo import EggInfoConverter
from .wheel import WheelConverter


class InstalledConverter(BaseConverter):
    lock = True

    _blacklist = {
        'pkg-resources',        # https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1635463
        'command-not-found',    # https://stackoverflow.com/a/22676267
    }

    def load_resolver(self, path=None, paths=None):
        if path is not None:
            root = self.load(path=path)
        else:
            root = self.load(paths=paths)
        return self._get_resolver(root)

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
            if 'dist-packages' in path.parts:
                continue

            if path.suffix == '.egg':
                name = canonicalize_name(path.with_suffix('').name.split('-')[0])
                if names is not None and name not in names:
                    continue

                # read *.egg dir
                egg_path = path / 'EGG-INFO'
                if not egg_path.exists():
                    continue
                subroot = EggInfoConverter().load_dir(egg_path)
                subroot.package = PackageRoot(path=path, name=root.name)
                if not subroot.package.packages:  # we cannot read single *.py file yet
                    continue
                deps = DependencyMaker.from_root(dep=subroot, root=root)
                for dep in deps:
                    if dep.name in self._blacklist:
                        continue
                    if dep.name in all_deps:
                        all_deps[dep.name] |= dep
                    else:
                        all_deps[dep.name] = dep
                continue

            # read site-packages / dist-packages
            for converter, pattern in parsers:
                for info_path in path.glob(pattern):
                    name = canonicalize_name(info_path.with_suffix('').name.split('-')[0])
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

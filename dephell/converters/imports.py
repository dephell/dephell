# built-in
import ast
from pathlib import Path
from typing import Dict, List, Set

# external
import requests
from dephell_discover import Root as PackageRoot

# app
from ..cache import TextCache
from ..controllers import DependencyMaker
from ..cached_property import cached_property
from ..models import RootDependency
from .base import BaseConverter


MAPPING_URLS = (
    'https://raw.githubusercontent.com/bndr/pipreqs/master/pipreqs/mapping',
    'https://raw.githubusercontent.com/JetBrains/intellij-community/master/python/helpers/tools/packages',
)
STDLIB_URL = 'https://raw.githubusercontent.com/bndr/pipreqs/master/pipreqs/stdlib'
CACHE_TTL = 3600 * 24 * 30  # 30 days


class ImportsConverter(BaseConverter):
    lock = True

    def can_parse(self, path: Path, content: str = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        if path.name == 'setup.py':
            return False
        return (path.suffix == '.py') or (path / '__init__.py').exists()

    def load(self, path) -> RootDependency:
        if isinstance(path, str):
            path = Path(path)
        if path.is_file():
            return self.loads(content=path.read_text(encoding='utf-8'))
        root = RootDependency(package=PackageRoot(path=path))

        # get modules
        modules = set()
        for package in root.package.packages:
            for module in package:
                content = module.read_text(encoding='utf-8')
                modules.update(self._get_modules(content=content))

        # attach modules
        local_modules = {package.module for package in root.package.packages}
        for module in sorted(modules):
            if module in local_modules:
                continue
            if Path(*module.split('.')).exists():
                continue
            root.attach_dependencies(DependencyMaker.from_params(
                source=root,
                raw_name=module,
                constraint='*',
            ))
        return root

    def loads(self, content: str) -> RootDependency:
        root = RootDependency()
        modules = self._get_modules(content=content)
        for module in sorted(modules):
            root.attach_dependencies(DependencyMaker.from_params(
                source=root,
                raw_name=module,
                constraint='*',
            ))
        return root

    def _get_modules(self, content) -> Set[str]:
        imports = set()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for subnode in node.names:
                    imports.add(subnode.name)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                imports.add(node.module)
        modules = set()
        for module in imports:
            if not module:
                continue
            module = module.split('.', maxsplit=1)[0]
            if module in self.stdlib:
                continue
            module = self.aliases.get(module, module)
            modules.add(module)
        return modules

    @cached_property
    def aliases(self) -> Dict[str, str]:
        cache = TextCache('imports', 'aliases', ttl=CACHE_TTL)
        lines = cache.load()
        if not lines:
            response = requests.get(MAPPING_URLS[0])
            lines = response.text.splitlines()
            cache.dump(lines)

        aliases = dict()
        for line in lines:
            if not line:
                continue
            alias, name = line.split(':')
            aliases[alias] = name
        return aliases

    @cached_property
    def stdlib(self) -> List[str]:
        cache = TextCache('imports', 'stdlib', ttl=-1)
        lines = cache.load()
        if lines:
            return lines

        response = requests.get(STDLIB_URL)
        lines = response.text.splitlines()
        cache.dump(lines)
        return lines

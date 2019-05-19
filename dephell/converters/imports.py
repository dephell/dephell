# built-in
import ast
from pathlib import Path
from typing import Dict, List, Set

# external
import requests
from dephell_discover import Root as PackageRoot

# app
from ..controllers import DependencyMaker
from ..utils import cached_property
from ..models import RootDependency
from .base import BaseConverter


MAPPING_URLS = (
    'https://raw.githubusercontent.com/bndr/pipreqs/master/pipreqs/mapping',
    'https://raw.githubusercontent.com/JetBrains/intellij-community/master/python/helpers/tools/packages',
)
STDLIB_URL = 'https://raw.githubusercontent.com/bndr/pipreqs/master/pipreqs/stdlib'


class ImportsConverter(BaseConverter):
    lock = True

    def can_parse(self, path: Path, content: str = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        return (path.suffix == '.py') or path.is_file()

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
                modules.extend(self._get_modules(content=content))

        # attach modules
        local_modules = {package.module for package in root.package.packages}
        for module in sorted(modules):
            if module in local_modules:
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
            elif isinstance(node, ast.ImportFrom):
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
        response = requests.get(MAPPING_URLS[0])
        aliases = dict()
        for line in response.text.splitlines():
            if not line:
                continue
            alias, name = line.split(':')
            aliases[alias] = name
        return aliases

    @cached_property
    def stdlib(self) -> List[str]:
        response = requests.get(MAPPING_URLS[0])
        return response.text.split()

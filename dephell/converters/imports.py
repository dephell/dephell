# built-in
import ast
from pathlib import Path

# external
# from dephell_discover import Root as PackageRoot
# from packaging.utils import canonicalize_name

# app
from ..models import RootDependency
from .base import BaseConverter


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
        ...

    def loads(self, content: str) -> RootDependency:
        ...

    @staticmethod
    def _get_modules(content):
        reqs = set()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for subnode in node.names:
                    reqs.add(subnode.name)
            elif isinstance(node, ast.ImportFrom):
                reqs.add(node.module)
        ...
        return reqs

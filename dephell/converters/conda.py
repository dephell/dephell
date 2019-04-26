from pathlib import Path
from typing import Optional

import yaml
from dephell_specifier import RangeSpecifier

from ..controllers import DependencyMaker
from ..models import RootDependency
from ..repositories import CondaRepo
from .base import BaseConverter


class CondaConverter(BaseConverter):
    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        return path.name in ('environment.yml', 'environment.yaml')

    def load(self, path) -> RootDependency:
        if isinstance(path, str):
            path = Path(path)
        with path.open('r', encoding='utf8') as stream:
            doc = yaml.safe_load(stream)
        root = RootDependency(raw_name=doc.get('name') or self._get_name(path=path))
        repo = CondaRepo(channels=doc.get('channels', []))
        for req in doc.get('dependencies', []):
            name, _sep, spec = req.partition('=')
            spec = '==' + spec if spec else '*'
            if name == 'python':
                root.python = RangeSpecifier(spec)
                continue
            root.attach_dependencies(DependencyMaker.from_params(
                raw_name=name,
                constraint=spec,
                repo=repo,
            ))
        return root

# built-in
import json
import pickle
from pathlib import Path
from time import time
from typing import List

# app
from .config import config
from .cached_property import cached_property


class BaseCache:
    ext = ''

    def __init__(self, *keys, ttl: int = -1):
        self.path = Path(config['cache']['path'], *keys)
        if self.ext:
            self.path = self.path.with_suffix(self.ext)
        self.ttl = ttl
        self._check_ttl()

    def _check_ttl(self) -> None:
        if self.ttl < 0:
            return
        if not self.path.exists():
            return
        if time() - self.path.stat().st_mtime > self.ttl:
            self.path.unlink()

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return '{}({})'.format(type(self), str(self.path))


class BinCache(BaseCache):
    ext = '.bin'

    def load(self):
        if not self.path.exists():
            return None
        with self.path.open('rb') as stream:
            return pickle.load(stream)

    def dump(self, data) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('wb') as stream:
            pickle.dump(data, stream)


class TextCache(BaseCache):
    ext = '.txt'

    def load(self):
        if not self.path.exists():
            return None
        with self.path.open('r') as stream:
            return stream.read().split('\n')

    def dump(self, data: List[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w') as stream:
            stream.write('\n'.join(data))


class JSONCache(BaseCache):
    ext = '.json'

    def load(self):
        if not self.path.exists():
            return None
        with self.path.open('r') as stream:
            try:
                return json.load(stream)
            except json.JSONDecodeError:
                return None
        return None

    def dump(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w') as stream:
            json.dump(data, stream)


class RequirementsCache(BaseCache):
    ext = '.txt'

    @cached_property
    def converter(self):
        from .converters import PIPConverter

        return PIPConverter(lock=False)

    def load(self):
        if not self.path.exists():
            return None
        root = self.converter.load(self.path)
        return root.dependencies

    def dump(self, root):
        from .models import Requirement

        self.path.parent.mkdir(parents=True, exist_ok=True)
        reqs = [Requirement(dep=dep, lock=False) for dep in root.dependencies]
        self.converter.dump(
            path=self.path,
            project=root,
            reqs=reqs,
        )

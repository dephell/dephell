# built-in
import json
import pickle
from pathlib import Path

from cached_property import cached_property

# app
from .config import config


class BaseCache:
    ext = ''

    def __init__(self, *keys):
        self.path = Path(config['cache'], *keys)
        if self.ext:
            self.path = self.path.with_suffix(self.ext)

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return '{}({})'.format(type(self), str(self.path))


class BinCache(BaseCache):
    ext = '.bin'

    def load(self):
        if self.path.exists():
            with self.path.open('rb') as stream:
                return pickle.load(stream)

    def dump(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('wb') as stream:
            pickle.dump(data, stream)


class TextCache(BaseCache):
    ext = '.txt'

    def load(self):
        if self.path.exists():
            with self.path.open('r') as stream:
                return stream.read().split('\n')

    def dump(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w') as stream:
            stream.write('\n'.join(data))


class JSONCache(BaseCache):
    ext = '.json'

    def load(self):
        if self.path.exists():
            with self.path.open('r') as stream:
                return json.load(stream)

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
            return
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

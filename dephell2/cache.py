import pickle
from pathlib import Path

cache_dir = './dephell'


class BaseCache:
    def __init__(self, *keys):
        self.path = Path(cache_dir)
        for key in keys:
            self.path /= key


class BinCache(BaseCache):
    def load(self):
        if self.path.exists():
            with self.path.open('rb') as stream:
                return pickle.load(stream)

    def dump(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('wb') as stream:
            pickle.dump(data, stream)


class TextCache(BaseCache):
    def load(self):
        if self.path.exists():
            with self.path.open('r') as stream:
                return stream.read().split('\n')

    def dump(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w') as stream:
            stream.write('\n'.join(data))

# built-in
import abc
from typing import Optional, Iterable, List, Dict


class Interface(metaclass=abc.ABCMeta):
    propagate = False

    @abc.abstractmethod
    def get_releases(self, dep) -> tuple:
        pass

    @abc.abstractmethod
    async def get_dependencies(self, name: str, version: str, extra: Optional[str] = None) -> tuple:
        pass

    @property
    def pretty_url(self):
        return self.url

    def search(self, query: Iterable[str]) -> List[Dict[str, str]]:
        raise NotImplementedError('search is unsupported by this repo')

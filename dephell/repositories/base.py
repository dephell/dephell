# built-in
import abc
from typing import Optional


class Interface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_releases(self, dep) -> tuple:
        pass

    @abc.abstractmethod
    async def get_dependencies(self, name: str, version: str, extra: Optional[str] = None) -> tuple:
        pass

    @property
    def pretty_url(self):
        return self.url

# built-in
import abc
import re
from typing import Optional, Iterable, List, Dict


REX_TOKEN = re.compile(r'^((?P<field>[a-z_]+)\:)?(?P<value>.+)$')


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

    @staticmethod
    def _parse_query(query: Iterable[str], default: str = 'name') -> Dict[str, str]:
        fields = dict()
        for token in query:
            group = REX_TOKEN.fullmatch(token).groupdict()
            fields[group['field'] or 'name'] = group['value']
        return fields

import abc


class Interface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_releases(self, dep) -> tuple:
        pass

    @abc.abstractmethod
    async def get_dependencies(self, name: str, version: str) -> tuple:
        pass

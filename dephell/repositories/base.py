import abc


class Interface(metaclass=abc.ABCMeta):

    # properties

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def hash(self):
        pass

    @abc.abstractproperty
    def link(self):
        pass

    # methods

    @abc.abstractmethod
    def get_releases(self, dep) -> tuple:
        pass

    @abc.abstractmethod
    async def get_dependencies(self, name: str, version: str) -> tuple:
        pass

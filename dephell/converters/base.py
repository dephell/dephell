# built-in
from os import unlink
from pathlib import Path
from tempfile import NamedTemporaryFile

# app
from ..constants import FILES
from ..controllers import Graph, Mutator, Resolver
from ..models import RootDependency


class BaseConverter:

    # root dependency load and dump

    def loads(self, content: str) -> RootDependency:
        stream = NamedTemporaryFile(mode='w', delete=False)
        stream.write(content)
        stream.close()
        root = self.load(stream.name)
        unlink(stream.name)
        return root

    def load(self, path) -> RootDependency:
        with open(str(path), 'r') as stream:
            return self.loads(stream.read())

    def dumps(self, reqs) -> str:
        raise NotImplementedError

    def dump(self, reqs, path):
        content = self.dumps(reqs=reqs)
        with open(str(path), 'w') as stream:
            stream.write(content)

    # resolver creation

    @staticmethod
    def _get_resolver(root: RootDependency) -> Resolver:
        return Resolver(
            graph=Graph(root),
            mutator=Mutator(),
        )

    def loads_resolver(self, content: str) -> Resolver:
        root = self.loads(content)
        return self._get_resolver(root)

    def load_resolver(self, path) -> Resolver:
        root = self.load(path)
        return self._get_resolver(root)

    # helpers

    @staticmethod
    def _get_name(*, path=None, content=None):
        if path is not None:
            path = Path(str(path))
            file_name = path.name
            project_name = path.name

            if file_name in FILES:
                return project_name
            return file_name

        if content is not None:
            return 'root-{}'.format(len(content))

# built-in
from os import unlink
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, Tuple, Union

# external
import attr

# app
from ..controllers import Graph, Mutator, Resolver
from ..models import RootDependency


@attr.s()
class BaseConverter:
    lock = attr.ib(type=bool, default=False)
    project_path = attr.ib(type=Optional[Path], default=None)
    resolve_path = attr.ib(type=Optional[Path], default=None)
    default_filename = attr.ib(type=Optional[str], default=None)

    _resolve_path = None

    # inspection

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        return False

    def copy(self, **kwargs) -> 'BaseConverter':
        params = attr.asdict(self, recurse=False)
        params.update(kwargs)
        return type(self)(**params)

    # root dependency load and dump

    def loads(self, content: str) -> RootDependency:
        """read dependencies from text
        """
        stream = NamedTemporaryFile(mode='w', delete=False)
        stream.write(content)
        stream.close()
        root = self.load(path=stream.name)
        unlink(stream.name)
        return root

    def load(self, path: Union[Path, str]) -> RootDependency:
        """read dependencies from file
        """
        if isinstance(path, str):
            path = Path(path)
        path = self._make_source_path_absolute(path)
        self._resolve_path = path.parent
        with path.open('r', encoding='utf8') as stream:
            root = self.loads(content=stream.read())
        self._resolve_path = None
        return root

    def dumps(self, reqs, *, project: RootDependency, content: str = None) -> str:
        raise NotImplementedError

    def dump(self, reqs, *, path, project: RootDependency) -> None:
        if isinstance(path, str):
            path = Path(path)
        path = self._make_source_path_absolute(path)

        # read
        if path.exists():
            with path.open('r', encoding='utf8') as stream:
                content = stream.read()
        else:
            content = None

        # make new content
        content = self.dumps(reqs=reqs, content=content, project=project)

        # write
        with path.open('w', encoding='utf8') as stream:
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
        root = self.load(path=path)
        return self._get_resolver(root)

    # helpers

    @staticmethod
    def _split_extra_and_marker(text: str) -> Tuple[str, Optional[str]]:
        text = text.lstrip('[').rstrip(']')
        if ':' not in text:
            return text, None
        extra, marker = text.split(':')
        if not extra:
            extra = 'main'
        return extra, marker

    @staticmethod
    def _make_path_absolute(root: Path, path: Path) -> Path:
        if path.is_absolute():
            return path
        root = root.resolve()
        return (root / path).resolve()

    def _make_source_path_absolute(self, path: Path) -> Path:
        root = self.project_path or Path()
        return self._make_path_absolute(root=root, path=path)

    def _make_dependency_path_absolute(self, path: Path) -> Path:
        root = self.resolve_path or self._resolve_path or self.project_path or Path()
        return self._make_path_absolute(root=root, path=path)

    def _make_dependency_path_relative(self, path: Path) -> Path:
        root = self.resolve_path or self._resolve_path or self.project_path or Path()
        root = root.resolve()
        return path.relative_to(str(root))

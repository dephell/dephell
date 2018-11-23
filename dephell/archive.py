# built-in
from contextlib import contextmanager
from fnmatch import fnmatch
from pathlib import Path, PurePath
from tarfile import TarFile
from zipfile import ZipFile

# external
import attr


NEW_PATH = Path('.dephell') / 'archives'


EXTRACTORS = {
    '.zip': ZipFile,
    '.whl': ZipFile,
    '.tar': TarFile.taropen,
    '.tar.gz': TarFile.gzopen,
    '.tar.bz2': TarFile.bz2open,
    '.tar.xz': TarFile.xzopen,
}


@attr.s()
class ArchiveStream:
    descriptor = attr.ib()
    cache_path = attr.ib()
    member_path = attr.ib()
    mode = attr.ib()

    def read(self):
        path = self.cache_path / self.member_path
        if path.exists():
            raise FileExistsError('file created between open and read')

        # extract to cache
        if hasattr(self.descriptor, 'getmember'):
            # tar
            member = self.descriptor.getmember(str(self.member_path))
        else:
            # zip
            member = self.descriptor.getinfo(str(self.member_path))
        self.descriptor.extract(member=member, path=str(self.cache_path))

        # read from cache
        with path.open(self.mode) as stream:
            return stream.read()


@attr.s()
class ArchivePath:
    archive_path = attr.ib()
    cache_path = attr.ib(default=None)
    member_path = attr.ib(factory=PurePath)
    _descriptor = attr.ib(default=None, repr=False)

    def __attrs_post_init__(self):
        if self.cache_path is None:
            self.cache_path = NEW_PATH / self.archive_path.name

    # properties

    @property
    def extractor(self):
        extension = ''.join(self.archive_path.suffixes)
        return EXTRACTORS[extension]

    # context managers

    @contextmanager
    def get_descriptor(self):
        if self._descriptor is not None:
            if hasattr(self._descriptor, 'closed'):
                is_closed = self._descriptor.closed  # tar
            else:
                is_closed = self._descriptor.fp  # zip
            if is_closed:
                yield self._descriptor
                return

        with self.extractor(str(self.archive_path)) as descriptor:
            self._descriptor = descriptor
            try:
                yield self._descriptor
            except Exception:
                self._descriptor = None
                raise

    @contextmanager
    def open(self, mode='r'):
        # read from cache
        path = self.cache_path / self.member_path
        if path.exists():
            with path.open() as stream:
                yield stream
        else:
            with self.get_descriptor() as descriptor:
                yield ArchiveStream(
                    descriptor=descriptor,
                    cache_path=self.cache_path,
                    member_path=self.member_path,
                    mode=mode,
                )

    # methods

    def iterdir(self, recursive=False):
        with self.get_descriptor() as descriptor:
            if hasattr(descriptor, 'getmembers'):
                members = descriptor.getmembers()   # tar
            else:
                members = descriptor.infolist()     # zip
            for member in members:
                name = getattr(member, 'name', None) or member.filename
                obj = self.__class__(
                    archive_path=self.archive_path,
                    cache_path=self.cache_path,
                    member_path=PurePath(name),
                )
                obj._descriptor = self._descriptor
                yield obj

    def glob(self, pattern):
        for path in self.iterdir(recursive=True):
            if fnmatch(name=str(path), pat=pattern):
                yield path

    # magic methods

    def __truediv__(self, key):
        obj = self.__class__(
            archive_path=self.archive_path,
            cache_path=self.cache_path,
            member_path=self.member_path / key,
        )
        obj._descriptor = self._descriptor
        return obj

    def __getattr__(self, name):
        return getattr(self.member_path, name)

    def __str__(self):
        return str(self.member_path)

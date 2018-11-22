from functools import partial
import tarfile
from zipfile import ZipFile
from pathlib import Path


NEW_PATH = Path('.dephell') / 'archives'


EXTRACTORS = {
    '.zip': ZipFile,
    '.whl': ZipFile,
    '.tar': partial(tarfile.open, mode='r:'),
    '.tar.gz': partial(tarfile.open, mode='r:gz'),
    '.tar.bz2': partial(tarfile.open, mode='r:bz2'),
    '.tar.xz': partial(tarfile.open, mode='r:xz'),
}


def extract(path: Path) -> Path:
    new_path = NEW_PATH / path.stem.stem
    extension = ''.join(path.suffixes)
    extractor = EXTRACTORS[extension]
    with extractor(str(path)) as archive:
        archive.extractall(new_path)
    return new_path

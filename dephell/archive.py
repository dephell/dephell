from tarfile import TarFile
from zipfile import ZipFile
from pathlib import Path
from typing import Optional, Iterable
from fnmatch import fnmatch


NEW_PATH = Path('.dephell') / 'archives'


EXTRACTORS = {
    '.zip': ZipFile,
    '.whl': ZipFile,
    '.tar': TarFile.taropen,
    '.tar.gz': TarFile.gzopen,
    '.tar.bz2': TarFile.bz2open,
    '.tar.xz': TarFile.xzopen,
}


def extract(
    path: Path,
    patterns: Optional[Iterable] = None,
    force: bool = False,
) -> Path:
    new_path = NEW_PATH / path.stem.stem
    if not force and new_path.exists:
        return new_path

    extension = ''.join(path.suffixes)
    extractor = EXTRACTORS[extension]

    with extractor(str(path)) as archive:
        if patterns is None:
            archive.extractall(new_path)
        else:
            for member in archive.getmembers():
                for pattern in patterns:
                    if fnmatch(name=member.name, pat=pattern):
                        archive.extract(member=member)
    return new_path

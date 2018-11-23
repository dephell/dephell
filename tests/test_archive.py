from pathlib import Path
from dephell.archive import ArchivePath


def test_open_zip(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'wheel.whl'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell' / '__init__.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from .controllers' in content


def test_open_tar_gz(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from setuptools import' in content


def test_glob_zip(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'wheel.whl'),
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/__init__.py'))
    assert len(paths) == 1
    assert str(paths[0]) == 'dephell/__init__.py'

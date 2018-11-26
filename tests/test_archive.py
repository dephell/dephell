# built-in
from pathlib import Path

import pytest

# project
from dephell.archive import ArchivePath, glob_path


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


def test_glob_tar(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/setup.py'))
    assert len(paths) == 1
    assert str(paths[0]) == 'dephell-0.2.0/setup.py'


def test_glob_dir(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('dephell-*/'))
    assert len(paths) == 1


def test_iterdir(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path
    assert 'dephell-0.2.0' in paths


@pytest.mark.parametrize("path,pattern,ok", [
    ('/lol/', '/lol/', True),
    ('/lol/', '/lal/', False),

    ('lol', '/lol/', True),
    ('lol', '/lal/', False),

    ('/lol/', '/l*', True),
    ('/tol/', '/l*', False),
    ('l', '/l*', True),
    ('lal', '/l*t', False),

    ('lol/lal', '*/lal', True),

    ('lol/lal', '**/lal', True),
    ('lol/lal', 'lol/**', True),
    ('lol/lal', 'lal/**', False),
])
def test_glob_path(path, pattern, ok):
    assert glob_path(path=path, pattern=pattern) is ok

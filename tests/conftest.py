# built-in
import shutil
from pathlib import Path

# external
import pytest


@pytest.fixture()
def temp_path(tmp_path: Path):
    for path in tmp_path.iterdir():
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(str(path))
    yield tmp_path

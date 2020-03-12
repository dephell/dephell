# built-in
from pathlib import Path

# external
import pytest

# project
from dephell.actions._entrypoints import _get_matching_path, get_entrypoints


@pytest.mark.parametrize('distinfo, pkg, match', [
    ('isort-4.3.21.dist-info', 'isort', True),

    ('flake8-3.7.9.dist-info', 'flake8', True),
    ('flake8-3.7.9.dist-info', 'flake8-isort', False),

    ('flake8_isort-2.7.0.dist-info', 'flake8-isort', True),
    ('flake8_isort-2.7.0.dist-info', 'flake8', False),

    # https://github.com/dephell/dephell/pull/380
    ('Sphinx-2.3.1.dist-info', 'sphinx', True),
    ('sphinxcontrib-2.3.1.dist-info', 'sphinx', False),
])
def test_get_matching_path(distinfo: str, pkg: str, match: bool):
    actual = _get_matching_path(paths=[Path(distinfo)], name=pkg)
    if match:
        assert actual is not None
        assert actual.name == distinfo
    else:
        assert actual is None


def test_smoke_get_entrypoints():
    class FakeVenv:
        lib_path = Path(pytest.__file__).parent.parent
        bin_path = None

    entrypoints = get_entrypoints(venv=FakeVenv, name='pytest')
    assert len(entrypoints) == 2
    assert {e.name for e in entrypoints} == {'pytest', 'py.test'}
    assert {e.path for e in entrypoints} == {'pytest:main'}

# external
import pytest
from dephell_markers import Markers
from dephell_specifier import RangeSpecifier

# project
from dephell.models import Dependency, Group, Release


@pytest.mark.parametrize('pdep, prel, ok', [
    ('>=2.7',           '<=3.4',        True),
    ('<=2.7',           '>=3.4',        False),

    # open intervals
    ('>=2.7',           '>=3.4',        True),
    ('>=3.4',           '>=2.7',        True),

    # one point intersection
    ('>=2.7,<=3.4',     '>=3.4',        True),
    ('>=2.7,<=3.4',     '>3.4',         False),
    ('>=3.4',           '>=2.7,<=3.4',  True),
    ('>3.4',            '>=2.7,<=3.4',  False),

    # version isn't exist
    ('>=2.7',           '<3.0',         True),
    ('>=2.8',           '<3.0',         False),
])
def test_python_compat(pdep: str, prel: str, ok: bool):
    dep = Dependency(
        raw_name='pathlib2',
        constraint=None,
        repo=None,
        marker=Markers(RangeSpecifier(pdep).to_marker('python_version')),
    )
    release = Release(
        raw_name='pathlib2',
        version='2.3.3',
        time=None,
        python=RangeSpecifier(prel),
    )
    dep.groups = [Group(number=1, releases=[release])]
    assert dep.python_compat is ok

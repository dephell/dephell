# project
from dephell.models import MarkerTracker


def test_apply():
    mt = MarkerTracker()
    mt.apply(source='sname', markers='python_version >= "3.5"')
    assert len(mt._markers) == 1
    assert str(mt._markers['sname']) == 'python_version >= "3.5"'


def test_str():
    mt = MarkerTracker()
    mt.apply(source='sname', markers='python_version >= "3.5"')
    assert str(mt) == 'python_version >= "3.5"'


def test_bool():
    mt = MarkerTracker()
    assert bool(mt) is False
    mt.apply(source='sname', markers='python_version >= "3.5"')
    assert bool(mt) is True

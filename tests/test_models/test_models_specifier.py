# built-in
from datetime import datetime

import pytest

# project
from dephell.models.release import Release
from dephell.models.specifier import Specifier


def test_version_compare():
    assert '3' in Specifier('>2')
    assert '2' not in Specifier('>2')

    assert '2.11.9' in Specifier('>2.9.0')
    assert '2.9.9' in Specifier('~=2.9.8')


def test_time_attach():
    time = datetime(2018, 9, 11, 12, 13)

    release = Release(raw_name='lol', version='1.2.3', time=time)
    spec = Specifier('>1.2.3')
    spec.attach_time([release])
    assert spec.time == time

    release = Release(raw_name='lol', version='1.2.3', time=time)
    spec = Specifier('>1.2.4')
    spec.attach_time([release])
    assert spec.time is None

    release = Release(raw_name='lol', version='1.2.4', time=time)
    spec = Specifier('>1.2.3')
    spec.attach_time([release])
    assert spec.time is None


def test_time_compare():
    time = datetime(2018, 9, 11, 12, 13)
    release = Release(raw_name='lol', version='1.2.3', time=time)
    spec = Specifier('>1.2.3')
    spec.attach_time([release])
    assert release not in spec

    time = datetime(2018, 9, 11, 12, 13)
    release = Release(raw_name='lol', version='1.2.3', time=time)
    spec = Specifier('>=1.2.3')
    spec.attach_time([release])
    assert release in spec

    time = datetime(2018, 9, 11, 12, 13)
    release = Release(raw_name='lol', version='1.2.3', time=time)
    spec = Specifier('==1.2.3')
    spec.attach_time([release])
    assert release in spec


@pytest.mark.parametrize('left, right, result', [
    # right
    ('<1.2',    '<1.4',     '<1.4'),
    ('<1.2',    '<=1.4',    '<=1.4'),

    # swap is not important
    ('<1.4',    '<1.2',     '<1.4'),
    ('<=1.4',   '<1.2',     '<=1.4'),

    # left
    ('>1.2',    '>1.4',     '>1.2'),
    ('>=1.2',   '>1.4',     '>=1.2'),

    # equal
    ('==1.2',   '<1.4',     '==1.2'),
    ('==1.2',   '<=1.4',    '==1.2'),
    ('>=1.2',   '==1.4',    '==1.4'),
    ('>1.2',    '==1.4',    '==1.4'),

    # common version
    ('==1.2',   '==1.2',    '==1.2'),
    ('<=1.2',   '==1.2',    '==1.2'),
    ('>=1.2',   '==1.2',    '==1.2'),
    ('<=1.2',   '>=1.2',    '==1.2'),

    # empty interval
    ('<=1.2',   '>=1.4',    None),
    ('<=1.2',   '>1.4',     None),
    ('<1.2',    '>=1.4',    None),
    ('==1.2',   '>=1.4',    None),
    ('==1.2',   '>1.4',     None),
    ('<=1.2',   '==1.4',    None),
    ('<1.2',    '==1.4',    None),

    # closed interval
    ('>=1.2',   '<=1.4',    None),
    ('>1.2',    '<1.4',     None),
    ('>=1.2',   '<1.4',     None),
    ('>1.2',    '<=1.4',    None),

])
def test_merge(left, right, result):
    ls = Specifier(left)
    rs = Specifier(right)
    if result is None:
        with pytest.raises(TypeError):
            ls + rs
    else:
        merged = ls + rs
        assert str(merged) == result

# built-in
from datetime import datetime

# external
from dephell_specifier import Specifier

# project
from dephell.models.release import Release


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

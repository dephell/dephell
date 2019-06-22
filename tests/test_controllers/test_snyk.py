import pytest

# project
from dephell.controllers import Snyk


@pytest.mark.allow_hosts()
def test_safety():
    snyk = Snyk()
    assert sum(len(vulns) for vulns in snyk.vulns.values()) == 50

    for name, vulns in snyk.vulns.items():
        assert len(snyk.get(name=name, version='0.0.0')) == len(vulns)

# project
import pytest
from dephell.controllers import Graph
from dephell.converters import PIPConverter, PIPFileConverter, PIPFileLockConverter
from dephell.models import Requirement


@pytest.mark.parametrize("converter,path", [
    (PIPConverter(lock=False), './tests/requirements/attrs-requests.txt'),
    (PIPConverter(lock=False), './tests/requirements/django-deal.txt'),
    (PIPConverter(lock=False), './tests/requirements/scipy-pandas-numpy.txt'),
    # (PIPConverter(lock=False), './tests/requirements/django-django.txt'),
    (PIPFileConverter(), './tests/requirements/pipfile.toml'),
    (PIPFileLockConverter(), './tests/requirements/pipfile.lock.json'),
])
def test_load_dump_load(converter, path):
    root1 = converter.load(path)
    reqs1 = Requirement.from_graph(graph=Graph(root1), lock=False)

    content = converter.dumps(reqs1, project=root1)
    root2 = converter.loads(content)
    reqs2 = Requirement.from_graph(graph=Graph(root2), lock=False)

    map1 = {req.name: req for req in reqs1}
    map2 = {req.name: req for req in reqs2}
    assert set(map1) == set(map2), 'loaded and dumped different deps set'

    exclude = {'sources'}
    for name, req1 in map1.items():
        req2 = map2[name]
        d1 = {k: v for k, v in req1 if k not in exclude}
        d2 = {k: v for k, v in req2 if k not in exclude}
        assert d1 == d2

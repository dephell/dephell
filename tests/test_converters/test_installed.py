# project
from dephell.converters.installed import InstalledConverter
from dephell.models import Requirement


def test_load():
    resolver = InstalledConverter().load_resolver()
    reqs = Requirement.from_graph(graph=resolver.graph, lock=True)
    reqs = {req.name: req for req in reqs}
    assert 'pytest' in reqs

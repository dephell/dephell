# project
from dephell.controllers import DependencyMaker
from dephell.models import RootDependency
from dephell.repositories import CondaRepo


def test_conda_get_releases():
    repo = CondaRepo(channels=['conda-forge'])
    root = RootDependency()
    dep = DependencyMaker.from_requirement(source=root, req='textdistance')[0]
    releases = repo.get_releases(dep=dep)
    versions = {str(release.version) for release in releases}
    assert not {'3.0.3', '3.1.0', '4.0.0', '4.1.0'} - versions

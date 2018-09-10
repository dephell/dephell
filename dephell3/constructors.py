from .models import Dependency, Constraint, Group, Release
from .repositories import WareHouseRepo


repo = WareHouseRepo()


def construct_dependency(name, spec):
    all_releases = repo.get_releases(name)

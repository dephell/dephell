from .dependency import Dependency
from .release import Release
from .repositories import WareHouseRepo


Dependency.repo = WareHouseRepo()
Release.repo = WareHouseRepo()


class Resolver:
    ...

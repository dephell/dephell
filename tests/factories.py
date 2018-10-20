from collections import defaultdict
from datetime import datetime
from packaging.requirements import Requirement

from dephell.models import Dependency, Release, RootDependency
from dephell.repositories import ReleaseRepo


DEFAULT_TIME = datetime(1970, 1, 1, 0, 0)


class Fake:
    def __init__(self, version, *deps):
        self.version = version
        self.deps = deps


def make_root(root, **releases) -> RootDependency:
    release_objects = []
    for name, fakes in releases.items():
        for fake in fakes:
            release = Release(
                raw_name=name,
                version=str(fake.version),
                time=DEFAULT_TIME,
            )
            release_objects.append(release)

    constraints = defaultdict(dict)
    for name, fakes in releases.items():
        for fake in fakes:
            constraints[name][fake.version] = tuple(Requirement(dep) for dep in fake.deps)

    repo = ReleaseRepo(*release_objects, deps=constraints)

    deps = []
    root_dep = RootDependency()
    root_dep.repo = repo
    for constr in root.deps:
        dep = Dependency.from_requirement(
            req=Requirement(constr),
            source=root_dep,
        )
        dep.repo = repo
        deps.append(dep)
    root_dep.attach_dependencies(deps)
    return root_dep

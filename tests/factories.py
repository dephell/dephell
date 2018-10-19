from datetime import datetime
from packaging.requirements import Requirement

from dephell.models import Dependency, Release, RootDependency
from dephell.repositories import ReleaseRepo


DEFAULT_TIME = datetime(1970, 1, 1, 0, 0)


def make_deps(root: dict, releases: dict, constraints: dict) -> RootDependency:
    release_objects = []
    for name, versions in releases.items():
        for version in versions:
            release = Release(
                raw_name=name,
                version=str(version),
                time=DEFAULT_TIME,
            )
            release_objects.append(release)

    for name, content in constraints.items():
        for version, constraint in content.items():
            constraints[name][version] = Requirement(constraint)

    repo = ReleaseRepo(*release_objects, deps=constraints)

    deps = []
    root_dep = RootDependency()
    for name, constr in root.items():
        dep = Dependency.from_params(
            raw_name=name,
            repo=repo,
            source=root_dep,
            constraint=constr,
        )
        deps.append(dep)
    root_dep.attach_dependencies(deps)
    return root_dep

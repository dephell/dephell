# built-in
from collections import defaultdict
from datetime import datetime
from unittest.mock import patch

# external
from packaging.requirements import Requirement as PackagingRequirement

# project
from dephell.controllers import DependencyMaker, Graph, Mutator, Resolver, analyze_conflict
from dephell.models import Release, Requirement, RootDependency
from dephell.repositories import ReleaseRepo


DEFAULT_TIME = datetime(1970, 1, 1, 0, 0)


class Fake:
    def __init__(self, version, *deps, extras=None):
        self.version = version
        self.deps = deps
        self.extras = extras or dict()

    def __repr__(self):
        return 'Fake(version={version}, deps={deps})'.format(
            version=self.version,
            deps=self.deps,
        )


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
            for extra in fake.extras:
                release = Release(
                    raw_name=name,
                    extra=extra,
                    version=str(fake.version),
                    time=DEFAULT_TIME,
                )

    constraints = defaultdict(dict)
    for name, fakes in releases.items():
        for fake in fakes:
            constraints[name][fake.version] = tuple(PackagingRequirement(dep) for dep in fake.deps)
            for extra, deps in fake.extras.items():
                cname = '{}[{}]'.format(name, extra)
                constraints[cname][fake.version] = tuple(PackagingRequirement(dep) for dep in deps)

    repo = ReleaseRepo(*release_objects, deps=constraints)

    deps = []
    root_dep = RootDependency(raw_name=''.join(sorted(releases)))
    root_dep.repo = repo
    for constr in root.deps:
        subdeps = DependencyMaker.from_requirement(
            req=PackagingRequirement(constr),
            source=root_dep,
        )
        for dep in subdeps:
            dep.repo = repo
        deps.extend(subdeps)
    root_dep.attach_dependencies(deps)
    return root_dep


def check(root, resolved=True, missed=None, **deps):
    resolver = Resolver(
        graph=Graph(root),
        mutator=Mutator(),
    )
    with patch(
        target='dephell.controllers._dependency.get_repo',
        return_value=resolver.graph._roots[0].repo,
    ):
        result = resolver.resolve(debug=True, silent=True)

    reqs = Requirement.from_graph(resolver.graph, lock=True)
    reqs = {req.name: req for req in reqs}

    try:
        assert result is resolved
    except AssertionError:
        if result is False:
            print(analyze_conflict(resolver=resolver))
        raise

    assert resolver.graph.applied

    for name in sorted(deps.keys()):
        if name not in reqs:
            raise AssertionError('Dep not in graph: ' + name)
        print(name, reqs[name].version)

    for name, version in deps.items():
        assert reqs[name].version == version, '{}: {} != {}'.format(name, reqs[name].version, version)

    if missed:
        for name in missed:
            assert name not in reqs

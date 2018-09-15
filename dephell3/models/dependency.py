from operator import attrgetter
from collections import defaultdict
import attr
import asyncio
from cached_property import cached_property
from packaging.utils import canonicalize_name
from .constraint import Constraint
from .group import Group
from ..repositories import get_repo
from copy import deepcopy


loop = asyncio.get_event_loop()


@attr.s()
class Dependency:
    raw_name = attr.ib()
    constraint = attr.ib(repr=False)
    repo = attr.ib(repr=False)
    url = attr.ib(repr=False)
    applied = attr.ib(default=False, repr=False)

    # constructors

    @classmethod
    def from_requirement(cls, source, req, url=None):
        # https://github.com/pypa/packaging/blob/master/packaging/requirements.py
        self = cls(
            raw_name=req.name,
            constraint=Constraint(source, req.specifier),
            repo=get_repo(url),
            url=url,
        )
        self._actualize_groups()
        return self

    # properties

    @cached_property
    def name(self) -> str:
        return canonicalize_name(self.raw_name)

    @cached_property
    def all_releases(self) -> tuple:
        return self.repo.get_releases(self.name)

    async def _fetch_releases_deps(self):
        tasks = []
        releases = []
        for release in self.all_releases:
            if 'dependencies' not in release.__dict__:
                task = asyncio.ensure_future(self.repo.get_dependencies(
                    release.name,
                    release.version,
                ))
                tasks.append(task)
                releases.append(release)
        responses = await asyncio.gather(*tasks)
        for release, response in zip(releases, responses):
            release.dependencies = response

    @cached_property
    def groups(self) -> tuple:
        # fetch releases
        future = asyncio.ensure_future(self._fetch_releases_deps())
        loop.run_until_complete(future)

        # group releases by their dependencies
        groups = defaultdict(set)
        for release in self.all_releases:
            key = '|'.join(sorted(map(str, release.dependencies)))
            groups[key].add(release)
        # sort groups by latest release
        groups = sorted(
            groups.values(),
            key=lambda releases: max(releases, key=attrgetter('time')),
            reverse=True,
        )
        # convert every group to Group object
        return tuple(
            Group(releases=releases, number=number)
            for number, releases in enumerate(groups)
        )

    @cached_property
    def group(self):
        """By first access choose and save best group
        """
        for group in self.groups:
            if not group.empty:
                return group

    @property
    def dependencies(self) -> tuple:
        constructor = self.__class__.from_requirement
        return tuple(constructor(self, req) for req in self.group.dependencies)

    @property
    def locked(self):
        return 'group' in self.__dict__

    @property
    def compat(self):
        # if group has already choosed
        if self.locked:
            return not self.group.empty
        # if group hasn't choosed
        for group in self.groups:
            if not group.empty:
                return True
        return False

    @property
    def used(self) -> bool:
        return not self.constraint.empty

    # methods

    def unlock(self):
        del self.__dict__['group']
        # if 'dependencies' in self.__dict__:
        #     del self.__dict__['dependencies']

    def merge(self, dep):
        self.constraint.merge(dep.constraint)
        self._actualize_groups()

    def unapply(self, name: str):
        self.constraint.unapply(name)
        self._actualize_groups()
        if self.locked:
            self.unlock()

    def copy(self):
        obj = deepcopy(self)
        obj.constraint = self.constraint.copy()
        if obj.locked:
            obj.unlock()
        return obj

    def _actualize_groups(self):
        filtrate = self.constraint.filter
        for group in self.groups:
            group.releases = filtrate(group.all_releases)

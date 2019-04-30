# built-in
import asyncio
from typing import Optional

# external
import attr

# app
from ..config import config
from ..utils import cached_property
from .group import Group


loop = asyncio.get_event_loop()


def get_key(release):
    return '|'.join(sorted(map(str, release.dependencies)))


@attr.s()
class Groups:
    dep = attr.ib()
    extra = attr.ib(type=Optional[str], default=None)

    _loaded_groups = attr.ib(factory=list)
    _loaded_releases_count = attr.ib(default=0)

    chunk_size = 20

    @cached_property
    def releases(self) -> tuple:
        releases = self.dep.repo.get_releases(self.dep)
        # sort
        reverse = True if config['strategy'] == 'max' else False
        releases = sorted(releases, reverse=reverse)
        # attach extra
        if self.extra is not None:
            for release in releases:
                release.extra = self.extra
        if not releases:
            raise LookupError('cannot find releases for ' + self.dep.name)
        return releases

    async def _fetch_all_deps(self, releases):
        tasks = []
        not_loaded_releases = []
        tasks_count = 0
        for release in releases:
            if 'dependencies' in release.__dict__:
                continue
            task = asyncio.ensure_future(self.dep.repo.get_dependencies(
                name=release.name,
                version=release.version,
                extra=self.extra,
            ))
            tasks.append(task)
            not_loaded_releases.append(release)
            tasks_count += 1
            if tasks_count >= self.chunk_size:
                break

        responses = await asyncio.gather(*tasks)
        for release, response in zip(not_loaded_releases, responses):
            release.dependencies = response

    async def _fetch_missed_deps(self, releases):
        if len(releases) <= 3:
            await self._fetch_all_deps(releases)
            return

        center = len(releases) // 2
        edges = (releases[0], releases[center], releases[-1])
        tasks = []
        for release in edges:
            task = asyncio.ensure_future(self.dep.repo.get_dependencies(
                name=release.name,
                version=release.version,
                extra=self.extra,
            ))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        keys = set()
        for release, response in zip(edges, responses):
            release.dependencies = response
            keys.add(get_key(release))

        if len(keys) == 1:
            response = responses[0]
            for release in releases:
                release.dependencies = response
            return

        await asyncio.gather(
            asyncio.ensure_future(self._fetch_missed_deps(releases[1:center])),
            asyncio.ensure_future(self._fetch_missed_deps(releases[center:-1])),
        )

    async def _fetch_releases_deps(self, releases=None):
        if releases is None:
            releases = self.releases

        if len(releases) <= 4:
            await self._fetch_all_deps(releases)
            return

        tasks = []
        missed = []
        for release in releases:
            # collect missed releases
            if 'dependencies' not in release.__dict__:
                missed.append(release)
                continue

            if not missed:
                left = release
                continue

            right = release
            if get_key(left) == get_key(right):
                # fill missed deps by edge deps
                for release in missed:
                    release.dependencies = left.dependencies
            else:
                # fetch missed releases
                tasks.append(
                    asyncio.ensure_future(
                        self._fetch_missed_deps(missed),
                    ),
                )
            left = right
            missed = []

        if missed:
            tasks.append(asyncio.ensure_future(self._fetch_missed_deps(missed)))
        await asyncio.gather(*tasks)

    def _load_release_deps(self, release) -> None:
        if release.dependencies is not None:
            return
        coroutine = self.dep.repo.get_dependencies(
            name=release.name,
            version=release.version,
            extra=self.extra,
        )
        gathered = asyncio.gather(coroutine)
        release.dependencies = loop.run_until_complete(gathered)[0]

    def _make_group(self, releases):
        group = Group(
            releases=releases,
            number=len(self._loaded_groups),
            dep=self.dep,
        )
        self._loaded_groups.append(group)
        self.actualize(group=group)
        return group

    def __iter__(self):
        # return all groups from cache
        for group in self._loaded_groups:
            self.actualize(group=group)
            yield group

        # load first group
        if not self._loaded_groups:
            release = self.releases[0]
            self._load_release_deps(release)
            self._loaded_releases_count += 1
            yield self._make_group([release])

        # load new groups
        prev_key = None
        releases = []
        for release in self.releases[self._loaded_releases_count:]:
            if 'dependencies' not in release.__dict__:
                future = asyncio.ensure_future(self._fetch_releases_deps())
                loop.run_until_complete(future)

            key = get_key(release)
            if prev_key is None:
                prev_key = key

            # collect releases with the same deps
            if key == prev_key:
                self._loaded_releases_count += 1
                releases.append(release)
                continue

            yield self._make_group(releases)
            prev_key = key
            self._loaded_releases_count += 1
            releases = [release]

        if releases:
            yield self._make_group(releases)

    def actualize(self, *, group=None) -> bool:
        if group:
            groups = [group]
        else:
            if not self._loaded_groups:
                return False
            groups = self._loaded_groups

        filtrate = self.dep.constraint.filter
        for group in groups:
            group.releases = filtrate(group.all_releases)
        return True

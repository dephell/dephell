import asyncio
from cached_property import cached_property
import attr

from .group import Group
from ..config import config

loop = asyncio.get_event_loop()


@attr.s()
class Groups:
    dep = attr.ib()

    _loaded_groups = attr.ib(factory=list)
    _loaded_releases_count = attr.ib(default=0)

    chunk_size = 10

    @cached_property
    def releases(self) -> tuple:
        releases = self.dep.repo.get_releases(self.dep)
        reverse = True if config['strategy'] == 'max' else False
        releases = sorted(releases, reverse=reverse)
        return releases

    async def _fetch_releases_deps(self):
        tasks = []
        releases = []
        tasks_count = 0
        for release in self.releases:
            if 'dependencies' not in release.__dict__:
                task = asyncio.ensure_future(self.dep.repo.get_dependencies(
                    release.name,
                    release.version,
                ))
                tasks.append(task)
                releases.append(release)
                tasks_count += 1
                if tasks_count == self.chunk_size:
                    break

        responses = await asyncio.gather(*tasks)
        for release, response in zip(releases, responses):
            release.dependencies = response

    def _load_release_deps(self, release) -> None:
        coroutine = self.dep.repo.get_dependencies(release.name, release.version)
        gathered = asyncio.gather(coroutine)
        release.dependencies = loop.run_until_complete(gathered)[0]

    def _make_group(self, releases):
        group = Group(
            releases=releases,
            number=len(self._loaded_groups),
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

            key = '|'.join(sorted(map(str, release.dependencies)))
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

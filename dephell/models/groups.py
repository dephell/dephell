import asyncio
from cached_property import cached_property
import attr

from .group import Group


loop = asyncio.get_event_loop()


@attr.s()
class Groups:
    dep = attr.ib()
    repo = attr.ib()

    _loaded_groups = attr.ib(factory=list)
    _loaded_releases_count = attr.ib(default=0)

    chunk_size = 10

    @cached_property
    def releases(self) -> tuple:
        return self.repo.get_releases(self.dep)

    async def _fetch_releases_deps(self):
        tasks = []
        releases = []
        tasks_count = 0
        for release in self.releases:
            if 'dependencies' not in release.__dict__:
                task = asyncio.ensure_future(self.repo.get_dependencies(
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
        coroutine = self.repo.get_dependencies(release.name, release.version)
        gathered = asyncio.gather(coroutine)
        release.dependencies = loop.run_until_complete(gathered)[0]

    def __iter__(self):
        # return all groups from cache
        yield from self._loaded_groups

        # load first group
        if not self._loaded_groups:
            release = self.releases[0]
            self._load_release_deps(release)
            group = Group(releases=[release], number=0)
            self._loaded_groups.append(group)
            self._loaded_releases_count += 1
            yield group

        # load new groups
        prev_key = None
        releases = []
        for release in self.all_releases[self._loaded_releases_count:]:
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

            group = Group(releases=releases, number=0)
            self._loaded_groups.append(group)
            yield group

            prev_key = key
            releases = [release]

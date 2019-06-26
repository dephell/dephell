import re
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple
from urllib.parse import urlparse

from dephell_markers import Markers
from packaging.requirements import InvalidRequirement, Requirement

from ..base import Interface
from ...cached_property import cached_property
from ...networking import aiohttp_session


try:
    import aiofiles
except ImportError:
    aiofiles = None


logger = getLogger('dephell.repositories.warehouse')
REX_WORD = re.compile('[a-zA-Z]+')


class WarehouseBaseRepo(Interface):
    # I'm not sure how to combine `@abstractproperty` and `= attr.ib()`
    @cached_property
    def prereleases(self) -> bool:
        raise NotImplementedError

    @cached_property
    def from_config(self):
        raise NotImplementedError

    @cached_property
    def repos(self):
        return [self]

    async def download(self, name: str, version: str, path: Path) -> bool:
        raise NotImplementedError

    @staticmethod
    def _convert_deps(*, deps, name, version, extra):

        # filter result
        result = []
        for dep in deps:
            try:
                req = Requirement(dep)
            except InvalidRequirement as e:
                msg = 'cannot parse requirement: {} from {} {}'
                try:
                    # try to parse with dropped out markers
                    req = Requirement(dep.split(';')[0])
                except InvalidRequirement:
                    raise ValueError(msg.format(dep, name, version)) from e
                else:
                    logger.warning('cannot parse marker', extra=dict(
                        requirement=dep,
                        source_name=name,
                        source_version=version,
                    ))

            try:
                dep_extra = req.marker and Markers(req.marker).extra
            except ValueError:  # unsupported operation for version marker python_version: in
                dep_extra = None

            # it's not extra and we want not extra too
            if dep_extra is None and extra is None:
                result.append(req)
                continue
            # it's extra, but we want not the extra
            # or it's not the extra, but we want extra.
            if dep_extra is None or extra is None:
                continue
            # it's extra and we want this extra
            elif dep_extra == extra:
                result.append(req)
                continue

        return tuple(result)

    async def _download_and_parse(self, *, url: str, converter) -> Tuple[str, ...]:
        with TemporaryDirectory() as tmp:
            fname = urlparse(url).path.strip('/').rsplit('/', maxsplit=1)[-1]
            path = Path(tmp) / fname
            await self._download(url=url, path=path)

            # load and make separated dep for every env
            root = converter.load(path)
            deps = []
            for dep in root.dependencies:
                if dep.envs == {'main'}:
                    deps.append(str(dep))
                else:
                    for env in dep.envs.copy() - {'main'}:
                        dep.envs = {env}
                        deps.append(str(dep))
            return tuple(deps)

    async def _download(self, *, url: str, path: Path) -> None:
        async with aiohttp_session(auth=self.auth) as session:
            async with session.get(url) as response:
                response.raise_for_status()

                # download file
                if aiofiles is not None:
                    async with aiofiles.open(str(path), mode='wb') as stream:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            await stream.write(chunk)
                else:
                    with path.open(mode='wb') as stream:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            stream.write(chunk)

    @staticmethod
    def _parse_name(fname: str) -> Tuple[str, str]:
        fname = fname.strip()
        if fname.endswith('.whl'):
            fname = fname.rsplit('-', maxsplit=3)[0]
            name, _, version = fname.partition('-')
            return name, version

        fname = fname.rsplit('.', maxsplit=1)[0]
        if fname.endswith('.tar'):
            fname = fname.rsplit('.', maxsplit=1)[0]
        parts = fname.split('-')
        name = []
        for part in parts:
            if REX_WORD.match(part):
                name.append(part)
            else:
                break
        version = parts[len(name):]
        return '-'.join(name), '-'.join(version)

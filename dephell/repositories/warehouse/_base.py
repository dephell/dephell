from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple

from aiohttp import ClientSession

from ..base import Interface


try:
    import aiofiles
except ImportError:
    aiofiles = None


class BaseWarehouse(Interface):

    async def _download_and_parse(self, *, url: str, converter) -> Tuple[str, ...]:
        with TemporaryDirectory() as tmp:
            async with ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError('invalid response: {} {} ({})'.format(
                            response.status, response.reason, url,
                        ))
                    path = Path(tmp) / url.rsplit('/', maxsplit=1)[-1]

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

            # load and make separated dep for every env
            root = converter.load(path)
            deps = []
            for dep in root.dependencies:
                for env in dep.envs.copy():
                    dep.envs = {env}
                    deps.append(str(dep))
            return tuple(deps)

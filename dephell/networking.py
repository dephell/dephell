# built-in
from functools import partial, update_wrapper
from logging import getLogger
from ssl import create_default_context
from time import sleep
from typing import Any, Optional

# external
import certifi
import requests
from aiohttp import ClientError, ClientSession, TCPConnector
from requests.sessions import Session

# project
from dephell.models.auth import Auth

# app
from . import __version__
from .config import config


USER_AGENT = 'DepHell/{version}'.format(version=__version__)
logger = getLogger('dephell.networking')


def aiohttp_session(*, auth: Optional[Auth] = None, **kwargs: Any) -> ClientSession:
    headers = {'User-Agent': USER_AGENT}
    if auth:
        headers['Authorization'] = auth.encode()

    # setup SSL
    cafile = config.get('ca')
    if not cafile:
        cafile = certifi.where()
    ssl_context = create_default_context(cafile=cafile)
    try:
        connector = TCPConnector(ssl=ssl_context)
    except TypeError:
        connector = TCPConnector(ssl_context=ssl_context)

    return ClientSession(headers=headers, connector=connector, **kwargs)


def requests_session(*, auth: Optional[Any] = None, headers: Optional[Any] = None, **kwargs: Any) -> Session:
    session = requests.Session()
    if auth:
        session.auth = auth

    # setup SSL
    cafile = config.get('ca')
    if cafile:
        session.verify = cafile

    # set headers
    if headers is None:
        headers = dict()
    headers.setdefault('User-Agent', USER_AGENT)
    session.headers = headers
    if kwargs:
        session.__dict__.update(kwargs)

    return session


def aiohttp_repeat(func=None, *, count: int = 4):
    if func is None:
        return partial(func, count=count)

    async def wrapper(*args: Any, **kwargs: Any) -> Optional[Any]:
        for pause in range(1, count + 1):
            try:
                return await func(*args, **kwargs)
            except ClientError:
                if pause == count:
                    raise
                logger.debug('aiohttp payload error, repeating...', exc_info=True)
                sleep(pause)
        raise RuntimeError('unreachable')

    wrapper = update_wrapper(wrapper=wrapper, wrapped=func)
    return wrapper

# built-in
from ssl import create_default_context

# external
import certifi
import requests
from aiohttp import ClientSession, TCPConnector

# app
from . import __version__


USER_AGENT = 'DepHell/{version}'.format(version=__version__)


def aiohttp_session(*, auth=None, **kwargs):
    headers = dict()
    if auth:
        headers['Authorization'] = auth.encode()
    ssl_context = create_default_context(cafile=certifi.where())
    try:
        connector = TCPConnector(ssl=ssl_context)
    except TypeError:
        connector = TCPConnector(ssl_context=ssl_context)
    return ClientSession(headers=headers, connector=connector, **kwargs)


def requests_session(*, auth=None, headers=None, **kwargs):
    session = requests.Session()
    if auth:
        session.auth = auth
    if headers is None:
        headers = dict()
    headers.setdefault('User-Agent', USER_AGENT)
    session.headers = headers
    if kwargs:
        session.__dict__.update(kwargs)
    return session

# built-in
from ssl import create_default_context

import certifi
from aiohttp import TCPConnector, ClientSession


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

import aiohttp
import asyncio
from aioresponses import aioresponses

loop = asyncio.get_event_loop()
session = aiohttp.ClientSession()
with aioresponses() as m:
    m.get('http://test.example.com', payload=dict(foo='bar'))

    resp = loop.run_until_complete(session.get('http://test.example.com'))
    data = loop.run_until_complete(resp.json())

    import pdb; pdb.set_trace()

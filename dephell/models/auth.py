from base64 import b64encode
from urllib.parse import urlparse

import attr
from requests.auth import HTTPBasicAuth


@attr.s(cmp=True, frozen=True)
class Auth(HTTPBasicAuth):
    hostname = attr.ib(type=str)
    username = attr.ib(type=str)
    password = attr.ib(type=str)
    encoding = attr.ib(type=str, default='latin1')

    # for requests
    def __call__(self, request):
        # additional check to prevent lack of creds
        if urlparse(request.url).hostname != self.hostname:
            return request

        request.headers['Authorization'] = self.encode()
        return request

    # for aiohttp
    def encode(self):
        creds = (self.username + ':' + self.password).encode(self.encoding)
        return 'Basic ' + b64encode(creds).decode('ascii')

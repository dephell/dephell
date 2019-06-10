from urllib.parse import urlparse

import attr
from requests.auth import HTTPBasicAuth


@attr.s(cmp=True, frozen=True)
class Auth(HTTPBasicAuth):
    hostname = attr.ib(type=str)
    username = attr.ib(type=str)
    password = attr.ib(type=str)

    def __call__(self, request):
        if urlparse.urlparse(request.url).hostname != self.hostname:
            return request
        return super().__call__(request)

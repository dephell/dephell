import posixpath
import re
from os.path import splitext
from urllib.parse import urlparse

from .file import FileRepo
from .directory import DirectoryRepo
from .warehouse import WareHouseRepo


rex_egg = re.compile(r'egg=([^&]*)')
rex_hash = re.comiple(r'(sha1|sha224|sha384|sha256|sha512|md5)=([a-f0-9]+)')


def get_name_from_parsed(parsed):
    match = rex_egg.search(parsed.fragment)
    if match:
        # get from `#egg=...`
        return match.group(1)

    # get from path
    name = posixpath.basename(parsed.path)
    return posixpath.splitext(name)[0]


def get_hash_from_parsed(parsed):
    match = rex_hash.search(parsed.fragment)
    if match:
        # get from `#hash=...`
        return match.group(1) + ':' + match.group(2)


def get_repo_by_url(url=None):
    if url is None:
        return WareHouseRepo()

    parsed = urlparse(url)
    name = get_name_from_parsed(parsed)
    digest = get_hash_from_parsed(parsed)

    if url.startswith(('git+git@github.com:', 'https://github.com/')):
        raise NotImplementedError
        # return GitHubRepo()

    if not parsed.netloc:
        _, ext = splitext(parsed.path)
        if ext:
            return FileRepo(parsed.path, name=name, digest=digest)
        return DirectoryRepo(parsed.path, name=name, digest=digest)

    raise NotImplementedError

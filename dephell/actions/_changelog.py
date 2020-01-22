from typing import Optional
from urllib.parse import urlparse

import requests


CHANGELOG_NAMES = (
    'changelog',
    'changes',
    'history',
    'news',
    'release',
    'releases',
    'whatsnew',
)

DOCS_NAMES = (
    'doc',
    'docs-src',
    'docs',
    'documentation',
    'wiki',
    '',
)

EXTENSIONS = (
    '.md',
    '.txt',
    '.rst',
    '',
)


def get_names():
    for ext in EXTENSIONS:
        for name in CHANGELOG_NAMES:
            yield name + ext
            yield name.upper() + ext
            yield name.title() + ext
            yield (name + ext).upper()


def known_domain(hostname: str) -> bool:
    if hostname == 'github.com':
        return True
    return False


def get_changelog_url(base_url) -> Optional[str]:
    parsed = urlparse(base_url)
    if not known_domain(parsed.hostname):
        return None
    response = requests.head(base_url)
    if not response.ok:
        return None
    base_url = response.url.rstrip('/').split('?')[0] + '/'

    if parsed.hostname == 'github.com':
        author, project, *_ = parsed.path.lstrip('/').split('/')
        tmpl = 'https://raw.githubusercontent.com/{}/{}/master/'
        base_url = tmpl.format(author, project)

    for name in get_names():
        for folder in DOCS_NAMES:
            path = '{}/{}'.format(folder, name).lstrip('/')
            url = base_url + path
            response = requests.head(url)
            if response.ok:
                return response.url

    return None

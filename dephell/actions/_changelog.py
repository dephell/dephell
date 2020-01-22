import re
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
    '',  # root goes first because sometimes changelog from root included in docs
    'docs',
    'doc',
    'wiki',
    'docs-src',
    'documentation',
)

EXTENSIONS = (
    '.md',
    '.txt',
    '.rst',
    '',
)
KNOWN_CHANGELOGS = {
    'pytest': 'https://raw.githubusercontent.com/pytest-dev/pytest/master/doc/en/changelog.rst',
}


def _get_names():
    for ext in EXTENSIONS:
        for name in CHANGELOG_NAMES:
            yield name + ext
    for ext in EXTENSIONS:
        for name in CHANGELOG_NAMES:
            yield name.upper() + ext
    for ext in EXTENSIONS:
        for name in CHANGELOG_NAMES:
            yield name.title() + ext
    for ext in EXTENSIONS:
        for name in CHANGELOG_NAMES:
            yield (name + ext).upper()


def _known_domain(hostname: str) -> bool:
    if hostname == 'github.com':
        return True
    return False


def _get_changelog_github(parsed) -> Optional[str]:
    # make URLs
    author, project, *_ = parsed.path.lstrip('/').split('/')
    if project in KNOWN_CHANGELOGS:
        return KNOWN_CHANGELOGS[project]
    tmpl = 'https://raw.githubusercontent.com/{}/{}/master/'
    raw_url = tmpl.format(author, project)
    tmpl = 'https://github.com/{}/{}/tree/master/'
    ui_url = tmpl.format(author, project)
    tmpl = '/{}/{}/blob/master/'
    blob_url = tmpl.format(author, project)

    for folder in DOCS_NAMES:
        # check if dir exists and get HTML of UI with the dir content
        response = requests.get(ui_url + folder)
        if not response.ok:
            continue

        # find if dir HTML page contains known link
        for name in _get_names():
            path = '{}/{}'.format(folder, name).lstrip('/')
            ui_path = blob_url + path
            if ui_path in response.text:
                return raw_url + path
    return None


def get_changelog_url(base_url) -> Optional[str]:
    parsed = urlparse(base_url)
    if not _known_domain(parsed.hostname):
        return None
    response = requests.head(base_url)
    if not response.ok:
        return None
    base_url = response.url.rstrip('/').split('?')[0] + '/'

    parsed = urlparse(base_url)
    if parsed.hostname == 'github.com':
        return _get_changelog_github(parsed)
    return None

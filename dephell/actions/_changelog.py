import re
from typing import Dict, Optional
from urllib.parse import urlparse

import requests


rex_version = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+')

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

    'docs/source',
    'doc/source',
    'wiki/source',
)

EXTENSIONS = (
    '.md',
    '.txt',
    '.rst',
    '',
)
KNOWN_CHANGELOGS = {
    # 'django': 'https://raw.githubusercontent.com/django/django/master/docs/releases/{}.txt',
    # 'flake8': 'https://gitlab.com/pycqa/flake8/raw/master/docs/source/release-notes/{}.rst',
    # 'numpy': 'https://raw.githubusercontent.com/numpy/numpy/master/doc/changelog/{}-changelog.rst',
    'pytest': 'https://raw.githubusercontent.com/pytest-dev/pytest/master/doc/en/changelog.rst',
    'py-trello': 'https://raw.githubusercontent.com/sarumont/py-trello/master/CHANGELOG',
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
    if hostname.startswith('www.'):
        hostname = hostname[4:]
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
        dir_response = requests.get(ui_url + folder)
        if not dir_response.ok:
            continue

        # lookup for known file names in the dir
        for name in _get_names():
            # find if dir HTML page contains the link
            path = '{}/{}'.format(folder, name).lstrip('/')
            ui_path = blob_url + path
            if ui_path not in dir_response.text:
                continue

            # check URL, it can be missed if the link on subdir instead of a file
            file_response = requests.get(raw_url + path)
            if not file_response.ok:
                continue
            return file_response.url
    return None


def get_changelog_url(base_url) -> Optional[str]:
    # fast checks for URL
    parsed = urlparse(base_url)
    if not _known_domain(parsed.hostname):
        return None
    response = requests.head(base_url)
    if not response.ok:
        return None
    base_url = response.url.rstrip('/').split('?')[0] + '/'

    # get hostname
    parsed = urlparse(base_url)
    hostname = parsed.hostname
    if hostname.startswith('www.'):
        hostname = hostname[4:]

    # select the best parser
    if hostname == 'github.com':
        return _get_changelog_github(parsed)
    return None


def _get_version(line: str) -> Optional[str]:
    line = line.strip()
    if not (3 <= len(line) < 40):
        return None

    if ':release:`' in line:
        return line.split(':release:`')[1].split()[0]

    if not (line[0].isdigit() or line[0].isalpha() or line[0] == '#'):
        return None

    match = rex_version.search(line)
    if match:
        return match.group(0)


def parse_changelog(content: str) -> Dict[str, str]:
    changelog = dict()

    version = None
    notes = []
    for line in content.splitlines():
        line = line.strip()
        new_version = _get_version(line=line)
        if not new_version:
            notes.append(line)
            continue

        if notes:
            changelog[version] = '\n'.join(notes)
        version = new_version
        notes = []
        continue

    if notes:
        changelog[version] = '\n'.join(notes)

    return changelog

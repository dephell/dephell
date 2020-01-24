# built-in
import re
from typing import Dict, Optional
from urllib.parse import urlparse

# external
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
    'alabaster': 'https://raw.githubusercontent.com/bitprophet/alabaster/master/docs/changelog.rst',
    'alembic': 'https://bitbucket.org/zzzeek/alembic/raw/master/docs/build/changelog.rst',
    'appenlight-client': 'https://raw.githubusercontent.com/AppEnlight/appenlight-client-python/master/CHANGELOG',  # noqa: E501
    'beautifulsoup4': 'https://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/download/head:/changelog-20090313220919-6rx0n6tw9wyjihv8-6/CHANGELOG',  # noqa: E501
    'cffi': 'https://bitbucket.org/cffi/release-doc/raw/default/doc/source/whatsnew.rst',
    'django-haystack': 'https://raw.githubusercontent.com/django-haystack/django-haystack/master/docs/changelog.rst',  # noqa: E501
    'django-hijack': 'https://raw.githubusercontent.com/arteria/django-hijack/master/CHANGELOG.txt',
    'django-registration': 'https://raw.githubusercontent.com/macropin/django-registration/master/CHANGELOG',
    'docutils': 'http://docutils.sourceforge.net/RELEASE-NOTES.txt',
    'genshi': 'https://genshi.edgewall.org/export/head/trunk/ChangeLog',
    'gitpython': 'https://raw.githubusercontent.com/gitpython-developers/GitPython/master/doc/source/changes.rst',  # noqa: E501
    'gunicorn': 'https://raw.githubusercontent.com/benoitc/gunicorn/master/docs/source/news.rst',
    'imapclient': 'https://raw.githubusercontent.com/mjs/imapclient/master/doc/src/releases.rst',
    'mako': 'https://raw.githubusercontent.com/sqlalchemy/mako/master/doc/build/changelog.rst',
    'py-trello': 'https://raw.githubusercontent.com/sarumont/py-trello/master/CHANGELOG',
    'pyinvoke': 'https://raw.githubusercontent.com/pyinvoke/invoke/master/sites/www/changelog.rst',
    'pytest': 'https://raw.githubusercontent.com/pytest-dev/pytest/master/doc/en/changelog.rst',
    'python-ldap': 'https://raw.githubusercontent.com/python-ldap/python-ldap/python-ldap-3.2.0/CHANGES',
    'python-memcached': 'https://raw.githubusercontent.com/linsomniac/python-memcached/master/ChangeLog',
    'pytz': 'https://raw.githubusercontent.com/stub42/pytz/master/tz/NEWS',
    'selenium': 'https://raw.githubusercontent.com/SeleniumHQ/selenium/master/py/CHANGES',
    'websocket-client': 'https://raw.githubusercontent.com/websocket-client/websocket-client/master/ChangeLog',  # noqa: E501
    'whitenoise': 'https://raw.githubusercontent.com/evansd/whitenoise/master/docs/changelog.rst',
}

PAGES = {
    'django-rest-framework': 'https://github.com/encode/django-rest-framework/tree/master/docs/community',
    'django': 'https://github.com/django/django/tree/master/docs/releases',
    'flake8': 'https://gitlab.com/pycqa/flake8/tree/master/docs/source/release-notes',
    'graphene': 'https://github.com/graphql-python/graphene/releases',
    'mccabe': 'https://github.com/PyCQA/mccabe/blob/master/README.rst',
    'numpy': 'https://github.com/numpy/numpy/tree/master/doc/changelog',
    'pandas': 'https://github.com/pandas-dev/pandas/tree/master/doc/source/whatsnew',
    'pyinotify': 'https://github.com/seb-m/pyinotify/wiki/Recent-Developments',
    'sqlalchemy': 'https://github.com/sqlalchemy/sqlalchemy/tree/master/doc/build/changelog',
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
    if hostname == 'pypi.org':
        return True
    return False


def _get_changelog_github(parsed) -> Optional[str]:
    # make URLs
    author, project, *_ = parsed.path.lstrip('/').split('/')
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


def _get_changelog_pypi(parsed) -> Optional[str]:
    project_name = parsed.path.strip('/').split('/')[1]
    project_name = project_name.lower().replace('_', '-')
    return KNOWN_CHANGELOGS.get(project_name)


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
    if hostname == 'pypi.org':
        return _get_changelog_pypi(parsed)
    return None


def _get_version(line: str) -> Optional[str]:
    line = line.strip()
    if not (3 <= len(line) < 40):
        return None

    if ':release:`' in line:
        return line.split(':release:`')[1].split()[0]

    if line.startswith(('Version ', 'Release ', ':version:', '.. scm-version-title:: ')):
        version = line.lstrip('. ').split()[1].lstrip('Vv.')
        if version[0].isdigit():
            return version

    match = rex_version.fullmatch(line.strip('#=*-v '))
    if match:
        return match.group(0)

    line = line.lstrip('# =')
    if not line:
        return None
    if not (line[0].isdigit() or line[0].isalpha()):
        return None

    match = rex_version.search(line)
    if match:
        return match.group(0)

    version = line.lstrip('Vv. ')
    if version[0].isdigit():
        return version.split()[0]

    return None


def parse_changelog(content: str) -> Dict[str, str]:
    changelog = dict()

    version = None
    notes = []
    for line in content.splitlines():
        # drop rst-like header from the section beginning
        if not notes:
            symbols = ''.join(set(line.strip()))
            if len(symbols) == 1 and symbols in '+-=':
                continue

        new_version = _get_version(line=line)
        if not new_version:
            notes.append(line)
            continue

        # save old section and start new one
        if notes:
            changelog[version] = '\n'.join(notes)
        version = new_version
        notes = []
        continue

    if notes:
        changelog[version] = '\n'.join(notes)

    return changelog

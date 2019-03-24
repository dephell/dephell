

# project
import pytest
from dephell.links.vcs import VCSLink


@pytest.mark.parametrize('url, params', [
    # https
    (
        'https://github.com/r1chardj0n3s/parse.git',
        dict(
            server='github.com',
            author='r1chardj0n3s',
            project='parse',
            vcs='git',
            protocol='https',
        ),
    ),
    (
        'https://gitlab.com/inkscape/inkscape.git',
        dict(
            server='gitlab.com',
            author='inkscape',
            project='inkscape',
            vcs='git',
            protocol='https',
        ),
    ),
    (
        'https://orsinium@bitbucket.org/mnpenner/merge-attrs',
        dict(
            server='bitbucket.org',
            author='mnpenner',
            project='merge-attrs',
            vcs='git',
            protocol='https',
            user='orsinium',
        ),
    ),
    # ssh
    (
        'git@github.com:r1chardj0n3s/parse.git',
        dict(
            server='github.com',
            author='r1chardj0n3s',
            project='parse',
            vcs='git',
            protocol='ssh',
            user='git',
        ),
    ),
    (
        'git@gitlab.com:inkscape/inkscape.git',
        dict(
            server='gitlab.com',
            author='inkscape',
            project='inkscape',
            vcs='git',
            protocol='ssh',
            user='git',
        ),
    ),
    (
        'ssh://hg@bitbucket.org/mnpenner/merge-attrs',
        dict(
            server='bitbucket.org',
            author='mnpenner',
            project='merge-attrs',
            vcs='git',
            protocol='ssh',
            user='hg',
        ),
    ),
    (
        'git@bitbucket.org:atlassian/python-bitbucket.git',
        dict(
            server='bitbucket.org',
            author='atlassian',
            project='python-bitbucket',
            vcs='git',
            protocol='ssh',
            user='git',
        ),
    ),
    # other info parsing
    (
        'hg+https://www.mercurial-scm.org/repo/hello',
        dict(
            server='www.mercurial-scm.org',
            author='repo',
            project='hello',
            vcs='hg',
            protocol='https',
        ),
    ),
    (
        'ssh://hg@bitbucket.org/mnpenner/merge-attrs#egg=merger',
        dict(
            server='bitbucket.org',
            author='mnpenner',
            project='merge-attrs',
            vcs='git',
            protocol='ssh',
            user='hg',
            name='merger',
        ),
    ),
    (
        'ssh://hg@bitbucket.org/mnpenner/merge-attrs@1.19',
        dict(
            server='bitbucket.org',
            author='mnpenner',
            project='merge-attrs',
            vcs='git',
            protocol='ssh',
            user='hg',
            rev='1.19',
        ),
    ),
])
def test_ssh_github(url, params):
    link = VCSLink.parse(url)
    for name, value in params.items():
        assert getattr(link, name) == value

import datetime
import os
import re
import sys
import time
from logging import getLogger
from platform import uname, python_version
from types import MappingProxyType, SimpleNamespace
from typing import Dict, List, Any

import attr
import requests
from jinja2 import Environment
from packaging.requirements import Requirement
from ruamel.yaml import YAML

from ..models.release import Release
from ..utils import cached_property


try:
    import yaml as pyyaml
except ImportError:
    pyyaml = None


# source: conda-build/metadata.py
# Selectors must be either:
# - at end of the line
# - embedded (anywhere) within a comment
#
# Notes:
# - [([^\[\]]+)\] means "find a pair of brackets containing any
#                 NON-bracket chars, and capture the contents"
# - (?(2)[^\(\)]*)$ means "allow trailing characters iff group 2 (#.*) was found."
#                 Skip markdown link syntax.
REX_SELECTOR = re.compile(r'(.+?)\s*(#.*)?\[([^\[\]]+)\](?(2)[^\(\)]*)$')


HISTORY_URL = 'https://api.github.com/repos/{repo}/commits?path={path}&per_page=100'
CONTENT_URL = 'https://raw.githubusercontent.com/{repo}/{rev}/{path}'

# https://conda.anaconda.org/conda-forge/linux-64
# https://conda.anaconda.org/conda-forge/noarch
# https://repo.anaconda.com/pkgs/main/linux-64
# https://repo.anaconda.com/pkgs/main/noarch
# https://repo.anaconda.com/pkgs/free/linux-64
# https://repo.anaconda.com/pkgs/free/noarch
# https://repo.anaconda.com/pkgs/r/linux-64
# https://repo.anaconda.com/pkgs/r/noarch


logger = getLogger('dephell.repositories.conda')


@attr.s()
class CondaRepo:
    channels = attr.ib(type=List[str])

    cookbooks = MappingProxyType({
        # https://github.com/conda-forge/textdistance-feedstock/blob/master/recipe/meta.yaml
        # https://github.com/conda-forge/ukbparse-feedstock/blob/master/recipe/meta.yaml
        'conda-forge': dict(repo='conda-forge/{name}-feedstock', path='recipe/meta.yaml'),
        # https://github.com/bioconda/bioconda-recipes/blob/master/recipes/anvio/meta.yaml
        'bioconda': dict(repo='bioconda/bioconda-recipes', path='recipes/{name}/meta.yaml'),
    })

    def get_releases(self, dep) -> tuple:
        revs = self._get_revs(name=dep.name)
        releases = dict()
        for rev in revs:
            # get metainfo
            try:
                meta = self._get_meta(rev=rev['rev'], repo=rev['repo'], path=rev['path'])
            except SyntaxError as e:
                logger.warning(str(e))
            version = str(meta['package']['version'])
            if version in releases:
                continue

            # make release
            release = Release(
                raw_name=dep.raw_name,
                version=version,
                time=rev['time'],
            )
            digest = meta.get('source', {}).get('sha256')
            if digest:
                release.hashes = (digest, )

            # get deps
            deps = []
            for req in meta.get('requirements', {}).get('run', []):
                parsed = self.parse_req(req)
                req = parsed['name'] + parsed.get('version', '')
                deps.append(Requirement(req))
            release.dependencies = tuple(deps)

            releases[version] = release

        return tuple(sorted(releases.values(), reverse=True))

    async def get_dependencies(self, *args, **kwargs):
        raise NotImplementedError('use get_releases to get deps')

    @staticmethod
    def parse_req(req: str) -> Dict[str, str]:
        req = req.split('#', 1)[0]
        req = req.split(' if ', 1)[0]
        req = req.rsplit(':', 2)[-1]

        # TODO: parse url

        # extract name
        req = req.strip()
        positions = [req.find(char) for char in '=<>!~ ']
        positions = [pos for pos in positions if pos >= 0]
        if positions:
            version_start = min(positions)
            name, req = req[:version_start], req[version_start:]
        else:
            name, req = req, ''
        name = name.strip()
        req = req.strip()
        if not req:
            return dict(name=name)

        # extract version and build
        # idk how this regex works
        # source: conda/models/match_spec.py
        match = re.search(r'((?:.+?)[^><!,|]?)(?:(?<![=!|,<>~])(?:[ =])([^-=,|<>~]+?))?$', req)
        if match:
            version, build = match.groups()
            if version is None:
                version = ''
            if build is None:
                build = ''
        else:
            version, build = req, ''
        version = version.strip()
        build = build.strip()

        # transform version to specifier
        if version[0] == '=' and version[1] != '=':
            version = '==' + version[1:]
        elif version[0] not in '=<>!~':
            version = '==' + version

        result = dict(name=name)
        if version:
            result['version'] = version
        if build:
            result['build'] = build
        return result

    # hidden methods

    def _get_revs(self, name: str) -> List[Dict[str, str]]:
        cookbooks = []
        for channel in self.channels:
            cookbook = self.cookbooks.get(channel)
            if cookbook:
                cookbooks.append(dict(
                    repo=cookbook['repo'].format(name=name),
                    path=cookbook['path'].format(name=name),
                ))
        if not cookbooks:
            cookbook = self.cookbooks['conda-forge']
            cookbooks.append(dict(
                repo=cookbook['repo'].format(name=name),
                path=cookbook['path'].format(name=name),
            ))

        revs = []
        for cookbook in cookbooks:
            url = HISTORY_URL.format(**cookbook)
            response = requests.get(url)
            if response.status_code != 200:
                continue
            for commit in response.json():
                revs.append(dict(
                    rev=commit['sha'],
                    time=datetime.datetime.strptime(
                        commit['commit']['author']['date'],
                        '%Y-%m-%dT%H:%M:%SZ',
                    ),
                    repo=cookbook['repo'],
                    path=cookbook['path'],
                ))
        return revs

    def _get_meta(self, rev: str, repo: str, path: str) -> Dict[str, Any]:
        # download
        url = CONTENT_URL.format(repo=repo, path=path, rev=rev)
        response = requests.get(url)
        response.raise_for_status()

        # render
        env = Environment()
        env.globals.update(dict(
            compiler=lambda name: name,
            pin_subpackage=lambda subpackage_name, **kwargs: subpackage_name,
            pin_compatible=lambda subpackage_name, **kwargs: subpackage_name,
            cdt=lambda package_name, **kwargs: package_name + '-cos6-aarch64',
            load_file_regex=lambda *args, **kwargs: None,
            datetime=datetime,
            time=time,
            target_platform='linux-64',
        ))
        template = env.from_string(response.text)
        content = template.render(
            os=SimpleNamespace(environ=os.environ, sep=os.path.sep),
            environ=os.environ,
        )

        # clean
        lines = []
        for line in content.split('\n'):
            match = REX_SELECTOR.match(line)
            if not match:
                lines.append(line)
                continue
            selector = match.group(3)
            if eval(selector, self._config):
                lines.append(line)
        content = '\n'.join(lines)

        # parse
        yaml = YAML(typ='safe')
        try:
            return yaml.load(content)
        except Exception as e:
            if pyyaml is not None:
                try:
                    return pyyaml.load(content)
                except Exception:
                    pass
            raise SyntaxError('cannot parse recipe: {}'.format(url)) from e

    @cached_property
    def _config(self):
        is_64 = sys.maxsize > 2**32
        translation = {
            'Linux': 'linux',
            'Windows': 'win',
            'darwin': 'osx',
        }
        system = translation.get(uname().system, 'linux')
        py = int(''.join(python_version().split('.')[:2]))

        return dict(
            linux=system == 'linux',
            linux32=system == 'linux' and not is_64,
            linux64=system == 'linux' and is_64,
            arm=False,
            osx=system == 'osx',
            unix=system in ('linux', 'osx'),
            win=system == 'win',
            win32=system == 'win' and not is_64,
            win64=system == 'win' and is_64,
            x86=True,
            x86_64=is_64,
            # os=os,
            environ=os.environ,
            nomkl=False,

            py=py,
            py3k=bool(30 <= py < 40),
            py2k=bool(20 <= py < 30),
            py26=bool(py == 26),
            py27=bool(py == 27),
            py33=bool(py == 33),
            py34=bool(py == 34),
            py35=bool(py == 35),
            py36=bool(py == 36),
            py37=bool(py == 37),
            py38=bool(py == 38),
        )

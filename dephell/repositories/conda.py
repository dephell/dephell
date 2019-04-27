import datetime
import time
import os
from types import MappingProxyType, SimpleNamespace
from typing import Dict, List, Any

import attr
import requests
from jinja2 import Environment
from packaging.requirements import Requirement
from ruamel.yaml import YAML

from ..models.release import Release


HISTORY_URL = 'https://api.github.com/repos/{repo}/commits?path={path}'
CONTENT_URL = 'https://raw.githubusercontent.com/{repo}/{rev}/{path}'

# https://conda.anaconda.org/conda-forge/linux-64
# https://conda.anaconda.org/conda-forge/noarch
# https://repo.anaconda.com/pkgs/main/linux-64
# https://repo.anaconda.com/pkgs/main/noarch
# https://repo.anaconda.com/pkgs/free/linux-64
# https://repo.anaconda.com/pkgs/free/noarch
# https://repo.anaconda.com/pkgs/r/linux-64
# https://repo.anaconda.com/pkgs/r/noarch


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
        yaml = YAML(typ='safe')
        return yaml.load(content)

    def get_releases(self, dep) -> tuple:
        revs = self._get_revs(name=dep.name)
        releases = dict()
        for rev in revs:
            meta = self._get_meta(rev=rev['rev'], repo=rev['repo'], path=rev['path'])
            version = meta['package']['version']
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
                deps.append(Requirement(req))
            release.dependencies = tuple(deps)
            releases[version] = release

        return tuple(sorted(releases.values(), reverse=True))

    async def get_dependencies(self, *args, **kwargs):
        raise NotImplementedError('use get_releases to get deps')

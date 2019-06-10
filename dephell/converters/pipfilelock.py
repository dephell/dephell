# built-in
import json
from collections import OrderedDict
from hashlib import sha256
from pathlib import Path
from typing import Optional

# external
from dephell_pythons import Pythons
from dephell_specifier import RangeSpecifier

# app
from ..controllers import RepositoriesRegistry
from ..models import RootDependency
from ..repositories import WarehouseBaseRepo, WarehouseLocalRepo
from .pipfile import PIPFileConverter


# https://stackoverflow.com/a/23820416
# https://github.com/pypa/pipfile/blob/master/examples/Pipfile.lock
# https://github.com/pypa/pipfile/blob/master/pipfile/api.py


class PIPFileLockConverter(PIPFileConverter):
    lock = True

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        if content:
            return ('pipfile-spec' in content and 'sha256' in content)
        else:
            return (path.name == 'Pipfile.lock')

    def loads(self, content) -> RootDependency:
        doc = json.loads(content, object_pairs_hook=OrderedDict)
        deps = []
        root = RootDependency()

        repo = RepositoriesRegistry()
        for repo_info in doc.get('_meta', {}).get('sources', []):
            repo.add_repo(name=repo_info['name'], url=repo_info['url'])
        repo.attach_config()

        python = doc.get('_meta', {}).get('requires', {}).get('python_version', '')
        if python not in {'', '*'}:
            root.python = RangeSpecifier('==' + python)

        for section, is_dev in [('default', False), ('develop', True)]:
            for name, content in doc.get(section, {}).items():
                subdeps = self._make_deps(root, name, content)
                # set repo
                if 'index' in content:
                    dep_repo = repo.make(name=content['index'])
                else:
                    dep_repo = repo
                for dep in subdeps:
                    if isinstance(dep.repo, WarehouseBaseRepo):
                        dep.repo = dep_repo
                # set envs
                for dep in subdeps:
                    dep.envs = {'dev'} if is_dev else {'main'}
                deps.extend(subdeps)
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        packages = {True: OrderedDict(), False: OrderedDict()}
        for req in reqs:
            packages[req.is_dev][req.raw_name] = dict(self._format_req(req=req))

        # get repos
        repos = []
        added_repos = set()
        for req in reqs:
            if not isinstance(req.dep.repo, WarehouseBaseRepo):
                continue
            for repo in req.dep.repo.repos:
                if repo.from_config:
                    continue
                if repo.name in added_repos:
                    continue
                # https://github.com/pypa/pipenv/issues/2231
                if isinstance(repo, WarehouseLocalRepo):
                    continue
                added_repos.add(repo.name)
                repos.append(OrderedDict([
                    ('url', repo.pretty_url),
                    ('verify_ssl', repo.pretty_url.startswith('https://')),
                    ('name', repo.name),
                ]))
        # pipenv doesn't work without explicit repo
        if not repos:
            repos.append(OrderedDict([
                ('url', 'https://pypi.org/simple/'),
                ('verify_ssl', True),
                ('name', 'pypi'),
            ]))

        python = Pythons(abstract=True).get_by_spec(project.python)
        data = OrderedDict([
            ('_meta', OrderedDict([
                ('sources', repos),
                ('requires', {'python_version': str(python.version)}),
            ])),
            ('default', packages[False]),
            ('develop', packages[True]),
        ])
        data['_meta']['hash'] = {'sha256': self._get_hash(data)}
        data['_meta']['pipfile-spec'] = 6
        return json.dumps(data, indent=4, separators=(',', ': '))

    @staticmethod
    def _get_hash(data: dict) -> str:
        content = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return sha256(content.encode('utf8')).hexdigest()

    def _format_req(self, req):
        result = dict()
        for name, value in req:
            if name == 'rev':
                name = 'ref'
            if name in self.fields:
                result[name] = value
        if isinstance(req.dep.repo, WarehouseBaseRepo) and req.dep.repo.name != 'pypi':
            result['index'] = req.dep.repo.name
        return result

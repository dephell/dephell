# built-in
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

# external
import tomlkit
from dephell_pythons import Pythons
from dephell_specifier import RangeSpecifier

# app
from ..controllers import DependencyMaker
from ..models import Constraint, Dependency, RootDependency
from ..repositories import WareHouseRepo, get_repo
from .base import BaseConverter


VCS_LIST = ('git', 'svn', 'hg', 'bzr')


class PIPFileConverter(BaseConverter):
    lock = False
    fields = (
        'version', 'editable', 'extras', 'markers',
        'ref', 'vcs', 'index', 'hashes',
        'subdirectory', 'path', 'file', 'uri',
        'git', 'svn', 'hg', 'bzr',
    )

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        if path.name == 'Pipfile':
            return True
        if content:
            if '[[source]]' in content and '[packages]' in content:
                return True
            if '[packages]' in content and '[dev-packages]' in content:
                return True
        return False

    def loads(self, content) -> RootDependency:
        doc = tomlkit.parse(content)
        deps = []
        root = RootDependency(self._get_name(content=content))

        repos = dict()
        if 'source' in doc:
            for repo in doc['source']:
                repos[repo['name']] = repo['url']

        python = doc.get('requires', {}).get('python_version', '')
        if python not in {'', '*'}:
            root.python = RangeSpecifier('==' + python)

        for section, is_dev in [('packages', False), ('dev-packages', True)]:
            for name, content in doc.get(section, {}).items():
                subdeps = self._make_deps(root, name, content)
                if 'index' in content:
                    repo_name = content.get('index')
                    for dep in subdeps:
                        dep.repo = WareHouseRepo(
                            name=repo_name,
                            url=repos[repo_name],
                        )
                for dep in subdeps:
                    # Pipfile doesn't support any other envs
                    dep.envs = {'dev'} if is_dev else {'main'}
                deps.extend(subdeps)
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        if content:
            doc = tomlkit.parse(content)
        else:
            doc = tomlkit.document()

        if 'source' not in doc:
            doc['source'] = tomlkit.aot()

        added_repos = {repo['name'] for repo in doc['source']}
        for req in reqs:
            if not isinstance(req.dep.repo, WareHouseRepo):
                continue
            if req.dep.repo.name in added_repos:
                continue
            added_repos.add(req.dep.repo.name)
            doc['source'].append(OrderedDict([
                ('name', req.dep.repo.name),
                ('url', req.dep.repo.pretty_url),
                ('verify_ssl', True),
            ]))

        if project.python:
            python = Pythons(abstract=True).get_by_spec(project.python)
            if 'requires' not in doc:
                doc['requires'] = tomlkit.table()
            doc['requires']['python_version'] = str(python.get_short_version())

        for section, is_dev in [('packages', False), ('dev-packages', True)]:
            # create section if doesn't exist
            if section not in doc:
                doc[section] = tomlkit.table()
                continue

            # clean packages from old packages
            names = {req.name for req in reqs if is_dev is req.is_dev}
            for name in doc[section]:
                if name not in names:
                    del doc[section][name]

        # write new packages
        for section, is_dev in [('packages', False), ('dev-packages', True)]:
            for req in reqs:
                if is_dev is req.is_dev:
                    doc[section][req.name] = self._format_req(req=req)

        return tomlkit.dumps(doc)

    # https://github.com/pypa/pipfile/blob/master/examples/Pipfile
    @staticmethod
    def _make_deps(root, name: str, content) -> List[Dependency]:
        if isinstance(content, str):
            return [Dependency(
                raw_name=name,
                constraint=Constraint(root, content),
                repo=get_repo(),
            )]

        # get link
        url = content.get('file') or content.get('path') or content.get('vcs')
        if not url:
            for vcs in VCS_LIST:
                if vcs in content:
                    url = vcs + '+' + content[vcs]
                    break
        if 'ref' in content:
            url += '@' + content['ref']

        # https://github.com/sarugaku/requirementslib/blob/master/src/requirementslib/models/requirements.py
        # https://github.com/pypa/pipenv/blob/master/pipenv/project.py
        return DependencyMaker.from_params(
            raw_name=name,
            # https://github.com/sarugaku/requirementslib/blob/master/src/requirementslib/models/utils.py
            constraint=Constraint(root, content.get('version', '')),
            extras=set(content.get('extras', [])),
            marker=content.get('markers'),
            url=url,
            editable=content.get('editable', False),
        )

    def _format_req(self, req):
        result = tomlkit.inline_table()
        for name, value in req:
            if name == 'rev':
                name = 'ref'
            if name in self.fields:
                if isinstance(value, tuple):
                    value = list(value)
                result[name] = value
        if 'version' not in result:
            result['version'] = '*'
        # if we have only version, return string instead of table
        if tuple(result.value) == ('version', ):
            return result['version']
        # do not specify version explicit
        if result['version'] == '*':
            del result['version']

        return result

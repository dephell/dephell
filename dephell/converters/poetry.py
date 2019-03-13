from typing import List

# external
import tomlkit

# app
from ..models import Constraint, Dependency, RootDependency, RangeSpecifier
from ..repositories import get_repo
from .base import BaseConverter


class PoetryConverter(BaseConverter):
    lock = False
    fields = (
        'version', 'python', 'platform', 'allows-prereleases',
        'optional', 'extras', 'develop',
        'git', 'branch', 'tag', 'rev',
        'file', 'path',
    )

    def loads(self, content) -> RootDependency:
        doc = tomlkit.parse(content)
        if 'tool' not in doc:
            doc['tool'] = {'poetry': tomlkit.table()}
        elif 'poetry' not in doc['tool']:
            doc['tool']['poetry'] = tomlkit.table()
        section = doc['tool']['poetry']

        deps = []
        root = RootDependency()
        if 'dependencies' in section:
            for name, content in section['dependencies'].items():
                if name == 'python':
                    continue
                deps.extend(self._make_deps(root, name, content))
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        if content:
            doc = tomlkit.parse(content)
        else:
            doc = tomlkit.document()
        if 'tool' not in doc:
            doc['tool'] = {'poetry': tomlkit.table()}
        elif 'poetry' not in doc['tool']:
            doc['tool']['poetry'] = tomlkit.table()
        section = doc['tool']['poetry']

        if 'dependencies' in section:
            # clean dependencies from old dependencies
            names = {req.name for req in reqs}
            section['dependencies'] = {
                name: info
                for name, info in section['dependencies'].items()
                if name in names
            }
            # write new dependencies to this table
            dependencies = section['dependencies']
        else:
            dependencies = tomlkit.table()

        for req in reqs:
            dependencies[req.name] = self._format_req(req=req)
        section['dependencies'] = dependencies

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
        url = content.get('file') or content.get('path')
        if not url and 'git' in content:
            url = 'git+' + content['git']
        rev = content.get('rev') or content.get('branch') or content.get('tag')
        if rev:
            url += '@' + rev

        # make marker
        markers = []
        # https://www.python.org/dev/peps/pep-0496/
        if 'platform' in content:
            markers.append('sys_platform == "{}" '.format(content['platform']))
        if 'python' in content:
            markers.append(RangeSpecifier(content['python']).to_marker('python_version'))
        ' and '.join(markers)

        return Dependency.from_params(
            raw_name=name,
            constraint=Constraint(root, content.get('version', '')),
            extras=set(content.get('extras', [])),
            marker=markers or None,
            url=url,
            editable=content.get('develop', False),
        )

    def _format_req(self, req):
        result = tomlkit.inline_table()
        for name, value in req:
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

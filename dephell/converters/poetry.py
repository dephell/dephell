# built-in
from collections import defaultdict
from typing import List

# external
import tomlkit

# app
from ..controllers import DependencyMaker
from ..models import Constraint, Dependency, EntryPoint, RangeSpecifier, RootDependency, Author
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
    _metafields = ('version', 'description', 'license', 'keywords', 'classifiers')

    def loads(self, content) -> RootDependency:
        doc = tomlkit.parse(content)
        if 'tool' not in doc:
            doc['tool'] = {'poetry': tomlkit.table()}
        elif 'poetry' not in doc['tool']:
            doc['tool']['poetry'] = tomlkit.table()
        section = doc['tool']['poetry']
        root = RootDependency()

        # read metainfo
        root.raw_name = section.get('name') or self._get_name(content=content)
        for field in self._metafields:
            if field in section:
                value = section[field]
                if isinstance(value, list):
                    value = tuple(value)
                setattr(root, field, value)
        if 'authors' in section:
            root.authors = tuple(Author.parse(author) for author in section['authors'])

        # read entrypoints
        root.entrypoints = []
        for name, content in section.get('scripts', {}).items():
            if isinstance(content, str):
                entrypoint = EntryPoint(name=name, path=content)
            else:
                entrypoint = EntryPoint(
                    name=name,
                    path=content['callable'],
                    extras=content['extras'],
                )
            root.entrypoints.append(entrypoint)
        for group_name, group_content in section.get('plugins', {}).items():
            for name, path in sorted(group_content.items()):
                root.entrypoints.append(EntryPoint(name=name, path=path, group=group_name))
        root.entrypoints = tuple(root.entrypoints)

        # read dependencies
        deps = []
        if 'dependencies' in section:
            for name, content in section['dependencies'].items():
                if name == 'python':
                    root.python = RangeSpecifier(content)
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

        # metainfo
        section['name'] = project.raw_name
        for field in self._metafields:
            value = getattr(project, field)
            if isinstance(value, tuple):
                value = list(value)
            if value:
                section[field] = value
            elif field in section:
                del section[field]
        if project.authors:
            section['authors'] = [str(author) for author in project.authors]
        elif 'authors' in section:
            del section['authors']
        self._add_entrypoints(section=section, entrypoints=project.entrypoints)

        # dependencies
        if 'dependencies' in section:
            # clean dependencies from old dependencies
            names = {req.name for req in reqs} | {'python'}
            for name in dict(section['dependencies']):
                if name not in names:
                    del section['dependencies'][name]
        else:
            section['dependencies'] = tomlkit.table()

        # python version
        section['dependencies']['python'] = str(project.python)

        for req in reqs:
            section['dependencies'][req.name] = self._format_req(req=req)
        return tomlkit.dumps(doc)

    @staticmethod
    def _add_entrypoints(section, entrypoints):
        # drop old console_scripts
        if 'scripts' in section:
            scripts = {e.name for e in entrypoints if e.group == 'console_scripts'}
            for script_name in section['scripts']:
                if script_name not in scripts:
                    del section['scripts'][script_name]

        # add console_scripts
        for entrypoint in entrypoints:
            if entrypoint.group != 'console_scripts':
                continue
            if 'scripts' not in section:
                section['scripts'] = tomlkit.table()
            if entrypoint.extras:
                content = tomlkit.inline_table()
                content['callable'] = entrypoint.path
                content['extras'] = entrypoint.extras
            else:
                content = entrypoint.path
            section['scripts'][entrypoint.name] = content

        # drop old plugins
        if 'plugins' in section:
            groups = defaultdict(set)
            for entrypoint in entrypoints:
                if entrypoint.group != 'console_scripts':
                    groups[entrypoint.group].add(entrypoint.name)
            for group_name, group_content in dict(section['plugins']):
                if group_name not in groups:
                    del section['plugins'][group_name]
                    continue
                for script_name in group_content:
                    if script_name not in groups[group_name]:
                        del section['plugins'][group_name][script_name]

        # add plugins
        for entrypoint in entrypoints:
            if entrypoint.group == 'console_scripts':
                continue
            if 'plugins' not in section:
                section['plugins'] = tomlkit.table()
            if entrypoint.group not in section['plugins']:
                section['plugins'][entrypoint.group] = tomlkit.table()
            section['plugins'][entrypoint.group][entrypoint.name] = entrypoint.path

    # https://github.com/sdispater/tomlkit/blob/master/pyproject.toml
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

        return DependencyMaker.from_params(
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

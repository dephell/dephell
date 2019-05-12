# built-in
from collections import defaultdict
from pathlib import Path
from typing import List, Optional

# external
import tomlkit
from dephell_links import DirLink
from dephell_specifier import RangeSpecifier

# app
from ..controllers import DependencyMaker
from ..models import Constraint, Dependency, RootDependency
from .base import BaseConverter


class PoetryLockConverter(BaseConverter):
    lock = True
    fields = (
        'category', 'description', 'name', 'marker', 'optional',
        'python-versions', 'version', 'dependencies',
    )
    # fields for dependency: python, version, platform

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        if content:
            return ('[[package]]' in content and '[metadata.hashes]' in content)
        else:
            return (path.name in ('pyproject.lock', 'poetry.lock'))

    def loads(self, content) -> RootDependency:
        doc = tomlkit.parse(content)
        root = RootDependency()
        root.python = RangeSpecifier(doc.get('metadata', {}).get('python-versions', '*'))

        envs = defaultdict(set)
        for extra, deps in doc.get('extras', {}).items():
            for dep in deps:
                envs[dep].add(extra)
        for content in doc.get('package', []):
            # category can be "dev" or "main"
            envs[content['name']].add(content['category'])

        for content in doc.get('package', []):
            root.attach_dependencies(self._make_deps(
                root=root,
                content=content,
                envs=envs[content['name']],
            ))
        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        doc = tomlkit.parse(content) if content else tomlkit.document()
        doc['package'] = [self._format_req(req=req) for req in reqs]

        # add extras
        extras = defaultdict(list)
        for req in reqs:
            if req.is_main:
                for extra in req.main_envs:
                    extras[extra].append(req.name)
            if req.is_dev:
                for extra in req.dev_envs:
                    extras[extra].append(req.name)
        if extras:
            doc['extras'] = dict(extras)

        doc['metadata'] = {
            # sha256 of tool.poetry section from pyproject.toml
            # 'content-hash': ...,
            # 'platform': '*',
            'python-versions': str(project.python),
        }

        doc['metadata']['hashes'] = tomlkit.table()
        for req in reqs:
            doc['metadata']['hashes'][req.name] = list(req.hashes or [])

        return tomlkit.dumps(doc)

    # https://github.com/sdispater/poetry/blob/master/poetry.lock
    @classmethod
    def _make_deps(cls, root, content, envs) -> List[Dependency]:
        # get link
        url = None
        if 'source' in content:
            url = content['source']['url']
            if content['source']['type'] == 'git':
                url = 'git+' + url
                if 'reference' in content['source']:
                    url += '@' + content['source']['reference']

        # make markers
        marker = content.get('marker', None)
        if content.get('python-versions', '*') != '*':
            python = RangeSpecifier(content['python-versions']).to_marker('python_version')
            if marker is None:
                marker = python
            else:
                marker = '({}) and {}'.format(marker, python)

        # make version
        version = content['version']
        if version != '*':
            version = '==' + version

        deps = DependencyMaker.from_params(
            raw_name=content['name'],
            description=content.get('description', ''),
            constraint=Constraint(root, version),
            marker=marker,
            url=url,
            editable=False,
            envs=envs,
        )

        if version == '*':
            return deps

        # add dependencies for dependencies
        subdeps = []
        for subname, subcontent in content.get('dependencies', dict()).items():
            if isinstance(subcontent, list):
                subcontent = ','.join(set(subcontent))
            if isinstance(subcontent, str):
                subdeps.extend(DependencyMaker.from_params(
                    raw_name=subname,
                    constraint=Constraint(root, '==' + subcontent),
                    envs=envs,
                ))
                continue

            if 'python' in subcontent:
                marker = RangeSpecifier(subcontent['python']).to_marker('python_version')
            else:
                marker = None

            if isinstance(subcontent['version'], list):
                subcontent['version'] = ','.join(set(subcontent['version']))
            subdeps.extend(DependencyMaker.from_params(
                raw_name=subname,
                constraint=Constraint(root, subcontent['version']),
                marker=marker,
                envs=envs,
            ))
        deps[0].dependencies = tuple(subdeps)

        return deps

    def _format_req(self, req):
        result = tomlkit.table()
        for name, value in req:
            if name in self.fields:
                if isinstance(value, tuple):
                    value = list(value)
                result[name] = value
        result['category'] = 'dev' if req.is_dev else 'main'
        if 'version' not in result:
            result['version'] = '*'
        result['version'] = result['version'].lstrip('=')
        if req.markers:
            result['marker'] = req.markers

        # add link
        if req.link:
            result['source'] = tomlkit.table()
            if req.git:
                result['source']['type'] = 'git'
            elif isinstance(req.link, DirLink):
                result['source']['type'] = 'directory'
            else:
                result['source']['type'] = 'legacy'
            result['source']['url'] = req.link.short
            if req.rev:
                result['source']['reference'] = req.rev

        # add dependencies
        deps = req.dep.dependencies
        if deps:
            result['dependencies'] = tomlkit.table()
            for dep in deps:
                result['dependencies'][dep.raw_name] = str(dep.constraint) or '*'

        return result
